"""CageCheck Inference explanation — fresh code, written 3 Nov 2026.

Vultr Serverless Inference is the mandatory LLM path for Challenge 1.
It explains a finding and suggests a safe replacement. It NEVER decides
block/approve — that decision is deterministic policy in policy.py.
If the Inference call fails, the policy decision stands and the caller
shows 'explanation unavailable — policy decision stands'.
Only redacted findings are sent to the model, never a raw secret and
never the full snippet if it matched a secret pattern.
"""
import json
import os
import urllib.request


def explain(finding, snippet_was_secret=False):
    base = os.environ.get("VULTR_INFERENCE_BASE_URL", "")
    key = os.environ.get("VULTR_INFERENCE_API_KEY", "")
    model = os.environ.get("VULTR_INFERENCE_MODEL", "")
    if not (base and key and model):
        return "[local mock — no Vultr Inference call] Policy decision stands. " \
               "On Vultr, Serverless Inference explains this finding and suggests a safe replacement."
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": "Explain a sandbox policy finding in 1-3 plain sentences and suggest a safe replacement. Do not invent a policy rule."},
            {"role": "user", "content": f"Finding (redacted): {finding}. Snippet contained a secret pattern: {snippet_was_secret}."},
        ],
        "max_tokens": 200,
    }
    try:
        req = urllib.request.Request(
            base.rstrip("/") + "/chat/completions",
            data=json.dumps(payload).encode(),
            headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode())
        return data["choices"][0]["message"]["content"].strip()
    except Exception:
        return "explanation unavailable — policy decision stands"
