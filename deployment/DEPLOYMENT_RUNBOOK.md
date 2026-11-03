# DEPLOYMENT RUNBOOK — CageCheck

> Status: **PLAN ONLY — NOT DEPLOYED.** No Vultr VM exists, no public
> demo URL exists, and no production smoke test has been run. This
> runbook is the reproducible plan from `VULTR_DEPLOY.md`, extended
> with the rulebook's manifest and rollback requirements. Do not quote
> this file as deploy evidence.

## 1. What is being deployed

- CageCheck web app: stdlib Python (`app/server.py`), single-column UI
  (`app/index.html`), deterministic policy (`app/policy.py`), local
  process+patch cage (`app/cage.py`), receipts + audit
  (`app/receipts.py`), Vultr Inference explanation only (`app/llm.py`).
- Intended target: Vultr Cloud Compute VM, Docker, HTTPS via a reverse
  proxy (Caddy or nginx). The real containment boundary on Vultr is a
  throwaway Docker container **per check**, destroyed after each check.
  That per-check wiring is a P0 deploy task — it is **not** wired in
  the current code, which only has the local process+patch cage.
- Source of truth: https://github.com/MSAbhishek22/cagecheck, branch
  `main`. Latest repo commit at gate-file time: `a5588ef` (no
  deployment exists to match it against — see RELEASE_MANIFEST.json).

## 2. Prerequisites (user taps, in order, before any deploy step)

Per `VULTR_DEPLOY.md`:

1. LabLab enrolment + Discord connection (registration closes at
   kickoff). Discord for the Vultr-enrolled LabLab account remains
   unconnected by user choice in the parent session — do not assume
   it is connected.
2. Vultr account on an email not previously associated with a Vultr
   account. **STOP at once if a card is asked.**
3. The $200 hackathon gift code shared at kickoff → Vultr Billing →
   Hackathon Promotion. **Never record the code value in any public
   file, and never record it in this runbook.**
4. Read the LabLab Rule Book and confirm in Discord: (a) India payout
   eligibility, (b) fresh-code / reuse rules. This build was written
   fresh in the event window, so it satisfies even a strict
   fresh-code rule — but record the confirmation verbatim anyway.
   **Both confirmations are still pending at gate-file time.**

## 3. Deploy steps (on the VM, after the taps above)

1. Create a Vultr Cloud Compute instance (Ubuntu LTS, smallest shape
   that runs Docker comfortably). Verify KVM availability and record
   the result (`ls /dev/kvm`): if KVM is absent, the isolation tier
   is Docker (not Firecracker/Kata) and the cage card must say so
   honestly. **KVM availability is unverified at gate-file time.**
2. Install Docker on the VM. Build from the repo: `docker build -t
   cagecheck .` (see `Dockerfile` in the repo).
3. Run the web app container, hardened, with **no secrets baked into
   the image**:
   - `--cap-drop=ALL --read-only
     --security-opt=no-new-privileges`, non-root user, no Docker
     socket mount, no `--pid=host`, no `--privileged`.
   - Port mapping for the app container (app port → host port).
   - Environment variables **by name only** (values live on the VM
     only, never in the repo, never in this runbook):
     - `HOST`
     - `PORT`
     - `CAGE_TIER` — must state the truthful tier once verified
       (target: `docker-per-check (throwaway container, destroyed
       after each check)`; do not set this value until it is true).
     - `VULTR_INFERENCE_BASE_URL`
     - `VULTR_INFERENCE_API_KEY`
     - `VULTR_INFERENCE_MODEL` — model id verified on Vultr at
       deploy time, not assumed in advance.
4. **P0 — wire the per-check cage:** the app container above runs the
   web app; the cage *inside* it must itself be a throwaway Docker
   container (or gVisor runtime) per check. Until this is wired and
   verified, **do not claim container-per-check isolation** and do
   not set `CAGE_TIER` to a container tier.
5. Reverse proxy (Caddy or nginx) for HTTPS → public demo URL.
6. Verify from **outside** the VM (see §5). A URL that only works
   from inside the VM is not a public demo URL.

## 4. Environment variables — names only, never values

| Variable | Purpose | Where set |
|---|---|---|
| `HOST` | Bind host for the web server (local default `127.0.0.1`; VM: `0.0.0.0`) | VM env / container env |
| `PORT` | Web server port (local default `8766`) | VM env / container env |
| `CAGE_TIER` | Truthful cage-tier string shown on `/health` | VM env / container env |
| `VULTR_INFERENCE_BASE_URL` | Vultr Serverless Inference endpoint | VM env only |
| `VULTR_INFERENCE_API_KEY` | Inference API key | VM env only, never in repo |
| `VULTR_INFERENCE_MODEL` | Inference model id, verified at deploy time | VM env only |

No `.env` file, key, token, or gift-code value may be committed or
written into this runbook.

## 5. Production health checks (all from outside the VM)

- [ ] Public URL loads the single-column UI.
- [ ] `GET /health` shows cage tier = the actual verified tier (target
      docker-per-check) and inference = `ok` (not `local-mock`).
- [ ] Attack preset (SSH read) → BLOCKED receipt, on the live URL.
- [ ] Policy-toggle preset → BLOCKED receipt, on the live URL.
- [ ] Clean preset → PASSED + approval receipt, on the live URL.
- [ ] Receipt lookup: a receipt id from the demo video returns the
      same slip on `/receipts/<id>`.
- [ ] Containers after a check: no leftover per-check container.
- [ ] Demo video recorded as a screen recording of the live URL
      (no slides-only, no local demo labelled as live).
- [ ] No secret values visible in the UI, receipts, or video frames.

None of these checks has been run against a production URL, because
no production URL exists.

## 6. Rollback and shutdown

- Rollback of a bad deploy: stop the app container, redeploy the last
  known-good repo commit, re-run §5. Do not hot-patch the VM by hand
  and leave the repo behind — the repo must stay the source of truth.
- **After judging: destroy the VM. Do not add a card to keep the
  deployment alive.** Repo + video + receipts remain as portfolio
  proof after the URL lapses.
- If the deployment lapses, the demo video and receipts remain valid
  only as a record of the deployment that existed; do not present a
  lapsed URL as live.

## 7. Exact blocker — deployment is BLOCKED

**Vultr billing requires linking a payment method for identity
verification. The user has no card. No card has been added, and no
card route is proposed here.**

Per the rulebook (§11) and the user's standing free-only rule, this
blocker does not authorise spending, a paid plan, or a card link.
The smallest compliant resolutions, in order, are:

1. A card-free Vultr verification path, if Vultr or the hackathon
   organisers confirm one exists (unverified at gate-file time —
   do not assume it).
2. A different free-tier host that still satisfies the Vultr Agent
   Rush requirement of a Vultr VM backend — **none is known**; the
   requirement names Vultr, so substituting another host would break
   hackathon-rule compliance and must not be done silently.
3. Accepting that CageCheck cannot be deployed for this hackathon
   window and recording the track as BLOCKED, with the repo + local
   tests + gate files kept as portfolio proof.

Until one of these resolves, `deployment/RELEASE_MANIFEST.json` keeps
deployed commit SHA, production URL, and timestamps at `null`, and
the overall release stays IN_PROGRESS, not COMPLETE.

## 8. Ownership

- Owner: M S Abhishek (repo owner MSAbhishek22).
- Repo: https://github.com/MSAbhishek22/cagecheck.
- This runbook was written from `VULTR_DEPLOY.md` + `README.md` +
  `app/server.py` on 3 Nov 2026. It is a plan, not a deploy receipt.
