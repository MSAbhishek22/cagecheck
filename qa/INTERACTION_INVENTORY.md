# INTERACTION INVENTORY — CageCheck

> Scope: every visible control in `app/index.html` plus every API route
> in `app/server.py`. Evidence is local only (this Linux sandbox,
> Python 3.12). No production URL exists, so no production evidence is
> claimed. Statuses: PASS / FAIL / BLOCKED per the rulebook.
>
> Verification re-run for this file (3 Nov 2026, local server
> `http://127.0.0.1:8766/`):
> - `python3 -m unittest discover -s tests` → **10/10 PASS**.
> - `GET /health` → `{"status": "ok", "cage": "local-process-patch
>   (NOT a container boundary — Docker on Vultr is the real boundary)",
>   "inference": "local-mock"}`.
> - SSH preset via `POST /api/check` → BLOCKED, rule
>   `secret_path_read`, receipt `CC-20261103-143255-3984`.
> - Full clean preset via `POST /api/check` → PASSED, rule `clean`,
>   cage output `60` (README's earlier local receipt for the same
>   preset was `CC-20261103-123520-F7F8`).
> - `POST /api/approve` on that BLOCKED receipt → 403
>   `Blocked snippets cannot be approved`.
> - Empty snippet → 400 `Paste a snippet first`; unknown receipt id →
>   404 `No receipt with that id`; `GET /receipts` returned 5 rows
>   (cumulative local audit log, gitignored — not repo content).
> - A deliberately incomplete clean snippet (`print(total(...))`
>   with no `total` defined) correctly returned HELD /
>   `runtime_error` (NameError) — the cage runs code, it does not
>   fake a pass.

## Visible controls (app/index.html)

| # | Control | Action | Expected behaviour | Actual implementation | Validation / error handling | Test evidence | Status |
|---|---|---|---|---|---|---|---|
| 1 | Paste box (`textarea#snippet`) | Type / paste a Python snippet | Accepts text, mono font, full width | Plain `textarea`, placeholder only | Server: empty → 400, >64 KiB → 400; client: no pre-validation, error shown as paragraph | Unit: policy/cage tests; curl: empty → 400 verified | PASS* (see note A) |
| 2 | "Check in cage" (`button.primary`) | Click → check snippet | POST `/api/check`, show stamp + receipt | `check()` fetches `/api/check`, renders stamp + receipt JSON, renders approve button iff stamp ≠ BLOCKED | Server errors shown as paragraph; **no loading state, no disabled state during fetch** — duplicate clicks send duplicate requests, each audited | Curl: SSH BLOCKED + clean PASSED verified | PASS* (see note B) |
| 3 | "Try the attack snippet" (`button.preset`) | Click → fill textarea | Fill attack snippet, do not run it | `setPreset('attack')` fills `open('/home/dev/.ssh/id_ed25519')` | None needed (fill only) | Curl of the filled snippet → BLOCKED verified | PASS |
| 4 | "Try to switch the cage off (from inside)" (`button.preset`) | Click → fill textarea | Fill policy-toggle snippet, do not run it | `setPreset('toggle')` fills `open('/app/policy.json', 'w')` | None needed (fill only) | Unit test `test_policy_toggle_write_blocked` PASS; README local verification BLOCKED | PASS |
| 5 | "Try a clean snippet" (`button.preset`) | Click → fill textarea | Fill clean snippet, do not run it | `setPreset('clean')` fills full `total()` function | None needed (fill only) | Curl of the filled snippet → PASSED, output `60` verified | PASS |
| 6 | "Approve clean snippet for repo" (`button.approve`, dynamic) | Click → approve a non-blocked receipt | POST `/api/approve`, append approval receipt; "cleared to copy, not sent anywhere" | `approve(id)` fetches `/api/approve`, appends returned JSON | Server: BLOCKED → 403, unknown id → 404; **client has no explicit error handling** — error JSON is appended in a receipt-styled block with no distinct error styling | Curl: approve BLOCKED → 403 verified; approve success path is code-reviewed, not curl-verified this session | PASS* (see notes C, D) |
| 7 | "Past receipts" link (`a href="#"`) | Click → list past receipts | Fetch `/receipts`, render id · stamp · rule · detail per row | `loadReceipts()` fetches `/receipts`, renders rows in `#receipts` | **No fetch-error handling, no empty-state handling** (empty log → heading only). `href="#"` + `return false` is a rulebook-banned pattern even though it works — see note E | Curl: `GET /receipts` returns rows verified | PASS* (see note E) |
| 8 | "Health (cage tier + Inference status)" link (`a href="/health"`) | Click → show cage tier + inference status | Show `/health` JSON | Plain link to `GET /health` (leaves the UI for raw JSON, no back link) | None | Curl: `/health` verified | PASS* (see note F) |
| 9 | Past-receipt list rows (display only) | (No click) | Click a row → full receipt slip | **No click handler.** Rows show id · stamp · rule · detail only; full slip is not reachable from the UI | N/A | API route exists (see below); UI lookup not wired | FAIL |

## API routes (app/server.py)

| Route | Behaviour | Validation / error handling | Test evidence | Status |
|---|---|---|---|---|
| `GET /` | Serves `app/index.html` | 404 for unknown paths | Served during curl verification | PASS |
| `GET /health` | `{"status": "ok", "cage": CAGE_TIER, "inference": "ok" if VULTR_INFERENCE_API_KEY else "local-mock"}` | None needed | Curl verified: local tier + `local-mock` | PASS |
| `GET /receipts` | Latest 50 audit rows, newest first | None | Curl verified: 5 rows | PASS |
| `GET /receipts/<id>` | Single receipt by id | Unknown id → 404 verified | 404 path verified; **200 path not exercised this session** | BLOCKED |
| `GET /audit` | Latest 100 audit rows, newest first | None | **Not exercised this session** (code exists, no curl/unit evidence) | BLOCKED |
| `POST /api/check` | Policy scan → cage run → stamp + receipt + audit append | Empty → 400, >64 KiB → 400, invalid JSON → treated as `{}` then 400 on empty | Unit 10/10; curl: BLOCKED / PASSED / HELD / 400 verified | PASS |
| `POST /api/approve` | Approval receipt for a non-blocked receipt; BLOCKED → 403 | Unknown id → 404, BLOCKED → 403 | Curl: BLOCKED → 403 verified; success path code-reviewed only | PASS* (see note D) |

## Notes — defects and gaps (none of these is a dead button)

- **Note A — textarea label:** no `<label>` element, placeholder only.
  Functional PASS, accessibility gap (see constitution §11).
- **Note B — no loading / disabled state:** "Check in cage" stays
  enabled during a fetch. Duplicate clicks create duplicate audit
  entries. Repeated-click behaviour is **untested**.
- **Note C — HELD approve label:** the approve button is labelled
  "Approve clean snippet for repo" for HELD results too, although the
  server approves HELD as `approved_clean_or_held`. The label
  overstates cleanliness for HELD and should read clean-or-held.
- **Note D — approve success path:** approve on a PASSED/HELD receipt
  was not curl-verified in this pass (only the 403 path was). The
  README's earlier local verification covers PASSED + approval, but
  this pass does not re-verify it.
- **Note E — `href="#"` pattern:** "Past receipts" uses `href="#"`
  with `onclick …; return false`. It works, but the rulebook bans
  `href="#"` in a final release — replace with a `<button>` or a real
  route before release.
- **Note F — Health link leaves the UI:** `GET /health` returns raw
  JSON with no back link; the user must use browser Back. Acceptable
  for an MVP, not a polished release behaviour.
- **No E2E suite:** there is no Playwright (or equivalent) test, no
  keyboard/focus test, no mobile/tablet test, and no Lighthouse run.
  UI controls are therefore verified by code reading + API curl only,
  not by an end-to-end journey test. This is why the overall control
  gate below is BLOCKED, not PASS.

## Dead controls found

**None.** Every visible button/link in `app/index.html` performs its
stated action when clicked (subject to the notes above). No
decorative button, empty handler, TODO handler, or fake success toast
was found.

## Untested / incomplete controls

- `GET /audit` (API only, no UI link) — not exercised this session.
- `GET /receipts/<id>` success (200) path — not exercised this session.
- `POST /api/approve` success path — not curl-verified this session.
- Keyboard operation, focus visibility, repeated-click behaviour,
  mobile/tablet viewports, Lighthouse, contrast measurement — none run.
- Past-receipt full-slip lookup from the UI — FAIL (row 9 above).

## Overall control gate

**BLOCKED** — no dead buttons, but E2E/keyboard/mobile evidence is
missing, one UI lookup (past-receipt full slip) is FAIL, and notes
B–F must be fixed before a release claim. Do not report
`ALL_VISIBLE_CONTROLS` as PASS until: an E2E journey test exists, the
HELD approve label is corrected, past-receipt rows link to full
slips, the `href="#"` is replaced, and a loading/disabled state is
added to "Check in cage".
