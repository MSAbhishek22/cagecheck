# DEMO VIDEO MANIFEST — CageCheck

> Status: **BLOCKED.** No demo video has been recorded from a live
> CageCheck deployment, because no live deployment exists. Do not
> attach any video URL to a CageCheck submission on the basis of this
> file.

## Current state (3 Nov 2026)

- Production URL: **null** (no Vultr VM deployed).
- Deployed commit SHA: **null** (repo commit `a5588ef` exists, but
  nothing is deployed to match it).
- Video file: **does not exist for CageCheck.** No local CageCheck
  video file exists in the project folder, and no local video may be
  presented as a live demo.
- Video URL (YouTube or other): **none. Do not invent one.**
- Recording date: **null**.
- Upload/publication status: **BLOCKED** (no video to upload, no
  live URL to record from).

## Why it is blocked

1. Vultr billing requires linking a payment method for identity
   verification; the user has no card, so the VM deploy is blocked
   (see `deployment/DEPLOYMENT_RUNBOOK.md` §7). No card route is
   proposed.
2. Per-check Docker container wiring is a P0 deploy task and is
   unverified, so even a deployed app could not yet be claimed to
   have container-per-check isolation.
3. No production smoke test has been run (see
   `deployment/RELEASE_MANIFEST.json` — local evidence only).

## Required order before any video is recorded

`Deploy → Verify Production → Freeze Release Commit → Record Demo
from Production URL → Review Video → Publish/Deliver Video → Attach
Verified Video URL`

## Required video content (when recording becomes possible)

Target 60–120 seconds (or the hackathon's specified duration), showing
on the verified production URL:

- The user problem (agent code runs as the user, with the user's
  credentials; a policy inside the agent's scope can be switched off).
- The core value: check the code in a cage before it touches the repo.
- The main journey: paste → check → stamp → receipt → approve
  (approve only for non-blocked results).
- The strongest differentiated feature: policy outside the cage, with
  a receipt naming the exact path, rule, and replay instruction.
- The containment moment required by Challenge 1: at least one
  BLOCKED receipt on camera (attack preset: SSH-key read, and
  policy-toggle preset if time allows).
- The meaningful 3D/spatial experience **only if it has been
  implemented by then** — it is currently PLANNED only (see
  `design/DESIGN_CONSTITUTION.md` §10) and must not be shown or
  claimed before then.
- A verifiable result: a receipt id visible on camera that returns
  the same slip on `/receipts/<id>`.
- A clear closing statement. No credentials, secrets, or gift-code
  values in any frame. Seeded/sample snippets must be identified as
  such; the presets are demo snippets, not real user code.

## What must NOT happen

- Do not record a slides-only, screenshot-assembled, or local-only
  video and attach it as a live demo.
- Do not submit the earlier local receipts (e.g.
  `CC-20261103-123520-472D`, `CC-20261103-143255-3984`) as Vultr
  receipts — they are local-run receipts.
- Do not claim a YouTube URL, an upload, or a publication without
  reading back and verifying the actual published/unlisted URL.
- If a video file is produced but publishing authorisation is
  unavailable, mark upload `BLOCKED_AUTHORIZATION` explicitly; do
  not claim the video gate passed.

## Update rule

When a production deployment is verified, this file must be updated
with: production URL, release version, deployed commit SHA, recording
date, actual video file path, duration, and verified video URL — and
the video must be re-recorded if production code changes materially
after recording.
