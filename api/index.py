"""CageCheck on Vercel — WSGI entrypoint (serverless adaptation).

The gate logic is unchanged (app/server.py: same policy scan, same
runtime cage, same receipts); this file is only a transport adapter.
Vercel's Python runtime calls `app(environ, start_response)`.

Serverless honesty notes (also in the submission draft):
- The audit log lives in /tmp on Vercel (the deployed filesystem is
  read-only elsewhere): set CAGECHECK_AUDIT_PATH=/tmp/cagecheck-audit.jsonl
  in the Vercel project. Receipts are therefore per-instance and
  ephemeral — a fresh instance starts with an empty receipt list. The
  verdict, receipt, and 403-on-BLOCKED-approve behaviour are identical.
- CAGE_TIER is set in the Vercel project to say "serverless-process":
  the cage is still a child Python process with the same restrictions,
  but it is NOT a container boundary (Docker per check is the real
  boundary, as the README states).
- No credentials are needed: without VULTR_INFERENCE_API_KEY the
  explanation is the labelled local mock, exactly as locally.
"""
import json
import os
import sys
import traceback

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.server import handle_get, handle_post  # noqa: E402

_STATUSES = {
    200: "200 OK",
    400: "400 Bad Request",
    403: "403 Forbidden",
    404: "404 Not Found",
    405: "405 Method Not Allowed",
    500: "500 Internal Server Error",
}


def app(environ, start_response):
    method = environ.get("REQUEST_METHOD", "GET").upper()
    path = environ.get("PATH_INFO", "/") or "/"
    # Defensive: if the platform ever passes the rewritten destination
    # path instead of the original request path, treat the function
    # root as the app root.
    if path in ("/api/index", "/api"):
        path = "/"
    try:
        if method == "GET":
            code, ctype, body = handle_get(path)
        elif method == "POST":
            try:
                length = int(environ.get("CONTENT_LENGTH") or 0)
            except ValueError:
                length = 0
            raw = environ["wsgi.input"].read(length) if length else b"{}"
            try:
                data = json.loads(raw.decode() or "{}")
            except Exception:
                data = {}
            code, ctype, body = handle_post(path, data)
        else:
            code, ctype, body = 405, "application/json", b'{"error": "method not allowed"}'
    except Exception:
        traceback.print_exc()
        code, ctype, body = 500, "application/json", b'{"error": "internal error"}'
    start_response(_STATUSES.get(code, f"{code} Unknown"),
                   [("Content-Type", ctype), ("Content-Length", str(len(body)))])
    return [body]
