"""CageCheck receipts — fresh code, written 3 Nov 2026 in the Vultr event window.

Every check, block, and approval produces a receipt. A receipt is the
record: receipt_id, timestamp, attempted action, blocked reason (or clean),
policy rule, redacted evidence, and a replay instruction pointing at the
audit log. Secrets are redacted BEFORE storage, not just before display.
"""
import datetime
import json
import os
import re
import uuid

SECRET_RE = re.compile(r"(AKIA[0-9A-Z]{16}|ghp_[A-Za-z0-9]{20,}|sk-[A-Za-z0-9\-_]{10,}|-----BEGIN [A-Z ]*PRIVATE KEY-----)")


def redact(text):
    if not text:
        return ""
    text = SECRET_RE.sub("[REDACTED]", str(text))
    return text[:200]


def new_id():
    stamp = datetime.datetime.now(datetime.timezone.utc).strftime("%Y%m%d-%H%M%S")
    return f"CC-{stamp}-{uuid.uuid4().hex[:4].upper()}"


def make_receipt(kind, snippet, verdict, rule, detail, cage_tier):
    return {
        "receipt_id": new_id(),
        "timestamp_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "kind": kind,  # check | approval
        "stamp": verdict,  # BLOCKED | HELD | PASSED
        "policy_rule": rule,
        "detail": redact(detail),
        "evidence": redact(snippet),
        "cage_tier": cage_tier,
        "replay": "Find this receipt_id in runs/audit.jsonl (kind=check or kind=approval) and re-run the same snippet via POST /api/check",
    }


def append_audit(audit_path, receipt):
    os.makedirs(os.path.dirname(audit_path), exist_ok=True)
    with open(audit_path, "a") as f:
        f.write(json.dumps(receipt) + "\n")


def load_audit(audit_path):
    if not os.path.exists(audit_path):
        return []
    rows = []
    with open(audit_path) as f:
        for line in f:
            line = line.strip()
            if line:
                try:
                    rows.append(json.loads(line))
                except Exception:
                    pass
    return rows
