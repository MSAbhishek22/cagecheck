"""CageCheck web app — fresh code, written 3 Nov 2026 in the Vultr event window.

Single-column UI, one paste box, one check, one stamp, one receipt.
Endpoints: GET / (UI), GET /health, GET /receipts, GET /receipts/<id>,
GET /audit, POST /api/check, POST /api/approve.
A blocked snippet has NO approval button and cannot be approved via API
either — POST /api/approve on a BLOCKED receipt returns 403.

Routing lives in handle_get / handle_post (transport-agnostic, so the
same logic serves both the local http.server Handler and the Vercel
WSGI entrypoint in api/index.py). AUDIT_PATH honours CAGECHECK_AUDIT_PATH
so serverless deploys (read-only filesystem except /tmp) can point the
audit log at a writable path; locally it defaults to runs/audit.jsonl.
"""
import json
import os
import traceback
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse

from app.cage import run_in_cage
from app.llm import explain
from app.policy import scan
from app.receipts import append_audit, load_audit, make_receipt

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
AUDIT_PATH = os.environ.get("CAGECHECK_AUDIT_PATH", os.path.join(BASE, "runs", "audit.jsonl"))
CAGE_TIER = os.environ.get("CAGE_TIER", "local-process-patch (NOT a container boundary — Docker on Vultr is the real boundary)")


def check_snippet(snippet):
    verdict, rule, detail = scan(snippet)
    if verdict == "BLOCKED":
        stamp = "BLOCKED"
        receipt = make_receipt("check", snippet, stamp, rule, detail, CAGE_TIER)
        receipt["explanation"] = explain(f"{rule}: {detail}", snippet_was_secret=("secret" in rule))
        append_audit(AUDIT_PATH, receipt)
        return receipt, 200
    # CLEAN or HELD: run in the cage; the runtime cage can still block.
    result = run_in_cage(snippet)
    if result.get("blocked"):
        stamp = "BLOCKED"
        receipt = make_receipt("check", snippet, stamp, "runtime_block", result["blocked"], CAGE_TIER)
        receipt["explanation"] = explain(f"runtime_block: {result['blocked']}")
        receipt["cage_output"] = result.get("output", "")
        append_audit(AUDIT_PATH, receipt)
        return receipt, 200
    if result.get("error"):
        stamp = "HELD"
        receipt = make_receipt("check", snippet, stamp, "runtime_error", result["error"], CAGE_TIER)
        receipt["explanation"] = explain(f"runtime_error: {result['error']}")
        receipt["cage_output"] = result.get("output", "")
        append_audit(AUDIT_PATH, receipt)
        return receipt, 200
    stamp = "PASSED" if verdict == "CLEAN" else "HELD"
    receipt = make_receipt("check", snippet, stamp, rule, detail, CAGE_TIER)
    receipt["explanation"] = explain(f"{rule}: {detail}")
    receipt["cage_output"] = result.get("output", "")
    append_audit(AUDIT_PATH, receipt)
    return receipt, 200


def _json(code, obj):
    return code, "application/json", json.dumps(obj).encode()


def handle_get(path):
    """Transport-agnostic GET routing. Returns (status, content_type, body)."""
    if path == "/":
        with open(os.path.join(BASE, "app", "index.html"), "rb") as f:
            return 200, "text/html", f.read()
    elif path == "/health":
        inference = "ok" if os.environ.get("VULTR_INFERENCE_API_KEY") else "local-mock"
        return _json(200, {"status": "ok", "cage": CAGE_TIER, "inference": inference})
    elif path == "/receipts":
        rows = load_audit(AUDIT_PATH)
        return _json(200, list(reversed(rows))[:50])
    elif path.startswith("/receipts/"):
        rid = path.split("/receipts/", 1)[1]
        for row in load_audit(AUDIT_PATH):
            if row.get("receipt_id") == rid:
                return _json(200, row)
        return _json(404, {"error": "No receipt with that id"})
    elif path == "/audit":
        return _json(200, list(reversed(load_audit(AUDIT_PATH)))[:100])
    return _json(404, {"error": "not found"})


def handle_post(path, body):
    """Transport-agnostic POST routing. `body` is the parsed JSON dict.
    Returns (status, content_type, body)."""
    if not isinstance(body, dict):
        body = {}
    if path == "/api/check":
        snippet = body.get("snippet_text", "")
        if not snippet.strip():
            return _json(400, {"error": "Paste a snippet first"})
        if len(snippet) > 64 * 1024:
            return _json(400, {"error": "Snippet too large (64 KiB limit)"})
        receipt, code = check_snippet(snippet)
        return code, "application/json", json.dumps(receipt).encode()
    elif path == "/api/approve":
        rid = body.get("receipt_id", "")
        for row in load_audit(AUDIT_PATH):
            if row.get("receipt_id") == rid:
                if row.get("stamp") == "BLOCKED":
                    return _json(403, {"error": "Blocked snippets cannot be approved"})
                approval = make_receipt("approval", row.get("evidence", ""), "APPROVED", "approved_clean_or_held", f"Approved receipt {rid} — cleared to copy, not sent anywhere", CAGE_TIER)
                approval["approved_receipt_id"] = rid
                append_audit(AUDIT_PATH, approval)
                return _json(200, approval)
        return _json(404, {"error": "No receipt with that id"})
    return _json(404, {"error": "not found"})


class Handler(BaseHTTPRequestHandler):
    def _send(self, code, obj, ctype="application/json"):
        body = obj if isinstance(obj, bytes) else json.dumps(obj).encode()
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        path = urlparse(self.path).path
        try:
            code, ctype, body = handle_get(path)
        except Exception:
            traceback.print_exc()
            code, ctype, body = 500, "application/json", b'{"error": "internal error"}'
        self._send(code, body, ctype)

    def do_POST(self):
        path = urlparse(self.path).path
        length = int(self.headers.get("Content-Length", 0) or 0)
        raw = self.rfile.read(length) if length else b"{}"
        try:
            body = json.loads(raw.decode() or "{}")
        except Exception:
            body = {}
        try:
            code, ctype, resp = handle_post(path, body)
        except Exception:
            traceback.print_exc()
            code, ctype, resp = 500, "application/json", b'{"error": "internal error"}'
        self._send(code, resp, ctype)

    def log_message(self, *args):
        pass


def main():
    host = os.environ.get("HOST", "127.0.0.1")
    port = int(os.environ.get("PORT", "8766"))
    print(f"CageCheck on http://{host}:{port}/  (cage tier: {CAGE_TIER})")
    ThreadingHTTPServer((host, port), Handler).serve_forever()


if __name__ == "__main__":
    main()
