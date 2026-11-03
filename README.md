# CageCheck — Check the agent's code in a cage before it touches your repo

> **Storyline:** You paste AI-written code into your repo every day. That code
> runs as you, with your credentials — and the sandbox setting you trust is
> a setting the agent can switch off (Forever Security, 29 Oct 2026).
> CageCheck is a cage whose policy lives *outside* the cage: paste a snippet,
> it is checked in a throwaway cage, and every block comes with a receipt
> naming the exact path, rule, and replay instruction. A clean snippet is
> the only snippet that can be approved. Nothing is sent anywhere —
> approval means "cleared to copy," not "sent."

**Vultr Agent Rush, Challenge 1 — Blast Radius Zero.** Fresh build, written
3 Nov 2026 in the event window (after the user's explicit "do it according
to you" approval of the strategist selection). No code from the 2 Nov
Containment Receipt Agent was copied into this repo.

## What it does (verified locally, 3 Nov 2026)
- Paste a Python snippet (or use a preset) → deterministic policy scan
  (before dispatch) → runtime cage run → stamp (PASSED / HELD / BLOCKED)
  → receipt slip (receipt_id, timestamp, rule, redacted evidence, replay).
- **Presets that work on the local server:**
  - Attack: `open('/home/dev/.ssh/id_ed25519')` → BLOCKED, rule
    `secret_path_read`, receipt names the path. Verified: receipt
    `CC-20261103-123520-472D` (local run, see runs/audit.jsonl).
  - Policy toggle: `open('/app/policy.json', 'w')` → BLOCKED (write
    outside cage). The policy file lives outside the cage directory and
    is not writable from inside it.
  - Clean: `total([10, 20, 30])` → PASSED, cage output `60`, approval
    button appears. A BLOCKED receipt returns 403 on
    `POST /api/approve` — blocked snippets cannot be approved.
- **Policy rules (deterministic, fail-closed):** secret-path reads,
  network connects/egress, subprocess/shell, destructive calls,
  secret env reads, writes/reads outside the cage. Network import with
  no connect attempt = HELD (approve only after review). Unlisted
  external effects = blocked + receipt.
- **Vultr Serverless Inference:** explains a finding and suggests a
  safe replacement. It NEVER decides block/approve. Locally, with no
  `VULTR_INFERENCE_*` env vars, the explanation is labelled
  `[local mock — no Vultr Inference call]`. On Vultr, set
  `VULTR_INFERENCE_BASE_URL`, `VULTR_INFERENCE_API_KEY`,
  `VULTR_INFERENCE_MODEL` on the VM only — never in the repo.

## Run it locally
```bash
cd ~/workspace/hackathons/cagecheck
python3 run.py
# open http://127.0.0.1:8766/  (PORT/HOST overridable)
# APIs: GET /health, GET /receipts, GET /receipts/<id>, GET /audit,
#       POST /api/check {"snippet_text": "..."}, POST /api/approve {"receipt_id": "..."}
```

## Tests (environment: this Linux sandbox, Python 3.12)
```bash
python3 -m unittest discover -s tests -v
```
Result 3 Nov 2026: **10/10 PASS** — policy rules (SSH, network,
subprocess, policy-toggle, clean, network-import-held), runtime cage
(clean run, dynamic-path SSH block, socket-import block), redaction.

## Architecture
```
Browser -> Web app (app/server.py, stdlib http.server)
  -> Policy engine (app/policy.py, deterministic, OUTSIDE the cage)
  -> Runtime cage (app/cage.py, child process, restricted imports/open,
       secret-scrubbed env, 5s / 256MB / 1MB limits)
  -> Receipts + audit log (app/receipts.py, runs/audit.jsonl, /receipts, /audit)
  -> Inference explanation (app/llm.py, Vultr Serverless Inference, explanation only)
```

## Honest limit — read this before judging
**Locally, this is process + patch isolation, NOT a kernel/container
boundary.** The real boundary is on Vultr: a throwaway Docker container
per check (see Dockerfile + VULTR_DEPLOY.md), destroyed after each
check, with `--cap-drop=ALL --read-only --security-opt=no-new-privileges`,
non-root user, no Docker socket mount, no `--pid=host`, no
`--privileged`. Until that VM deploy is verified, this build is a
**local MVP, not a live demo** — do not submit it as a live demo, and
do not present local receipts as Vultr receipts.

## What is NOT done (and why)
- **No Vultr VM deploy, no public demo URL, no public GitHub repo, no
  demo video recorded from Vultr, no LabLab submission.** All need the
  user's own accounts and, for the video/URL, a real Vultr VM.
- **No LabLab / Discord / Vultr account created by the assistant.**
  Accounts need the user's own email, password, and legal ticks.
- **No card added, ever.** Free-only rule: $200 gift code at kickoff
  on a fresh email, let the deployment lapse after judging.
- **No secrets in this repo.** `.gitignore` excludes `.env`, keys,
  and run logs. The cage never receives credentials.

## Strategist pack
The full ABHI_22 strategist process for this idea (intelligence report,
18-idea long list, scoring 82/100, adversarial review, design
constitution, product/architecture/build plan, demo script, pitch,
submission checklist) is at
`~/workspace/hackathons/vultr-agent-rush/strategist/`.
