# VULTR_DEPLOY.md — CageCheck (NOT YET DEPLOYED)

## Status: NOT DEPLOYED
No Vultr VM exists yet. This file is the deploy plan, not a deploy receipt.
Do not claim a live demo URL until the verify checklist below is checked
from outside the VM.

## User taps (in order, before any deploy step)
1. LabLab enrolment + Discord connection — before Tue 3 Nov 2026 20:30 IST
   (registration closes at kickoff).
2. Vultr account on a fresh email (not previously associated with a
   Vultr account). STOP at once if a card is asked.
3. $200 gift code shared at kickoff → Vultr Billing → Hackathon
   Promotion. Do not record the code value in any public file.
4. Read the LabLab Rule Book + confirm in Discord: (a) India payout
   eligibility, (b) fresh-code / reuse rules. This build is fresh in
   the event window, so it satisfies even a strict fresh-code rule —
   but record the confirmation verbatim anyway.

## Deploy steps (on the VM, after the taps above)
1. Create a Vultr Cloud Compute instance (Ubuntu LTS, smallest shape
   that runs Docker comfortably). Verify KVM availability:
   `ls /dev/kvm` — record the result; if KVM is absent, the isolation
   tier is Docker (not Firecracker/Kata) and the receipt's cage card
   must say so honestly.
2. Install Docker on the VM. Build: `docker build -t cagecheck .`
3. Run (hardened, no secrets baked in):
   ```
   docker run --cap-drop=ALL --read-only --security-opt=no-new-privileges \
     -p 8080:8080 -e HOST=0.0.0.0 -e PORT=8080 \
     -e CAGE_TIER="docker-per-check (throwaway container, destroyed after each check)" \
     -e VULTR_INFERENCE_BASE_URL=https://api.vultrinference.com/v1 \
     -e VULTR_INFERENCE_API_KEY='<from VM env only, never in repo>' \
     -e VULTR_INFERENCE_MODEL='<model id verified on Vultr at deploy time>' \
     cagecheck
   ```
   Note: the container above runs the web app. The *per-check* cage
   inside it must itself be a throwaway Docker container (or gVisor
   runtime) — wiring that per-check container is a P0 deploy task,
   not an assumption. Until it is wired and verified, do not claim
   container-per-check isolation.
4. Reverse proxy (Caddy or nginx) for HTTPS → public demo URL.
5. Public GitHub repo (MIT) with this code + README (Vultr services,
   architecture, use case). No 2 Nov code in the repo.

## Verify checklist (all from OUTSIDE the VM — a URL that only works
## from inside the VM is not a public demo URL)
- [ ] Public URL loads the single-column UI
- [ ] GET /health shows cage tier = docker-per-check (or the actual tier)
      and inference = ok (not local-mock)
- [ ] Attack preset (SSH read) → BLOCKED receipt, on the live URL
- [ ] Policy-toggle preset → BLOCKED receipt, on the live URL
- [ ] Clean preset → PASSED + approval receipt, on the live URL
- [ ] Receipt lookup: a receipt id from the demo video returns the
      same slip on /receipts/<id>
- [ ] Containers after a check: no leftover per-check container
- [ ] Demo video recorded as a screen recording of the live URL
      (no slides-only, no local demo labelled as live)

## After judging
Destroy the VM. Do not add a card to keep the deployment alive.
Repo + video + receipts remain as portfolio proof after the URL lapses.
