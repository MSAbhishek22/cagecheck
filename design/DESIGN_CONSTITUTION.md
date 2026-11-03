# DESIGN CONSTITUTION — CageCheck

> Status: this constitution describes the **actual built UI** in
> `app/index.html` as of 3 Nov 2026, not the aspirational strategist draft.
> Where the built UI differs from the strategist draft, the built UI wins
> and the difference is stated. No design claim in this file is based on a
> site inspected in this gate pass — see §12 (design research) for the
> honest research status.

## 1. Product personality and emotional tone

A border inspector's stamp desk, not a hacker's terminal and not a SaaS
dashboard. Calm, procedural, a little severe. Nothing glows, nothing
pulses, nothing pretends to be intelligent. The intelligence is in the
procedure, and the procedure is visible: paste → check → stamp → receipt
→ approve (only if not blocked).

## 2. Target user and context of use

A developer about to paste AI-suggested code into a repo, and a judge
watching a screen share. The primary viewing context is a laptop screen
share: the whole decision must be readable in one scroll, with no tab
hunting. The user pastes untrusted code; the tool must never send that
code anywhere. Approval means "cleared to copy", never "sent".

## 3. Visual metaphor — cage + stamp + receipt

- **Cage:** a dashed-border card, always visible, listing what the cage
  does for every check (throwaway per check, network off, secret env
  scrubbed, policy outside the cage, 5s / 256 MB / 1 MB / 64 KiB caps).
  The cage is a visible border in the UI, not just a word in the copy.
- **Stamp:** a circular, rotated stamp mark carrying one word:
  PASSED, HELD, or BLOCKED. The stamp is the decision, made visible.
- **Receipt:** a white, monospace slip (JSON) naming receipt_id,
  timestamp, stamp, policy rule, redacted detail/evidence, cage tier,
  replay instruction, and explanation. A receipt you can quote back.

## 4. Colour palette — semantic roles (actual CSS values)

| Token | Value | Semantic role | Where used |
|---|---|---|---|
| Paper | `#F7F4ED` | Page background, receipt-like warmth | `body` background |
| Ink | `#1A1A18` | Primary text, cage outline, primary button | Text, cage border, `button.primary` |
| Paper-white | `#FFFFFF` | Input, cage card, receipt surface | `textarea`, `.cage`, `.receipt` |
| Secondary grey | `#444444` / `#555555` | Tagline and small print | `p.tag`, `.small` |
| Border grey | `#6B6B66` | Input and preset-button borders | `textarea`, `button.preset` |
| Receipt border | `#D8D3C8` | Receipt slip outline | `.receipt` |
| Stamp red | `#B42318` | BLOCKED | `.stamp` (default) |
| Stamp green | `#1F6B3A` | PASSED | `.stamp.pass` |
| Stamp amber | `#8A6D00` | HELD, and approval-button outline | `.stamp.held`, `button.approve` |

Rules: stamp colours are used **only** for the stamp and the approval
outline, never as a full-panel background fill. No gradients,
glassmorphism, glow, or dark-mode-by-default anywhere. Stamp meaning is
never colour-only: the word PASSED / HELD / BLOCKED is always printed
in the stamp itself.

## 5. Typography — actual built stacks (not the strategist draft)

The strategist draft proposed Fraunces / Source Serif, Inter / Source
Sans, and JetBrains Mono / IBM Plex Mono as webfonts. **The built UI
does not download any webfont** (no CDN, no font files). It uses
system stacks:

- Headings: `Georgia, serif` — `h1` 32px, `h2` 16px.
- Body: `Inter, system-ui, sans-serif` — tagline 16px, cage list 14px,
  small print 13px.
- Code / receipts / stamps: `ui-monospace, Menlo, monospace` —
  textarea 14px, receipt 13px, stamp bold with 1px letter-spacing.
- Stamp rotation: `rotate(-6deg)`, 4px border, `border-radius: 50%`.

Do not claim the strategist font choices are in the built UI. If a
future release adopts webfonts, this section must be updated and the
no-CDN constraint re-checked.

## 6. Layout grid and page composition — actual order

Single column, centred, `max-width: 720px`, page padding `24px 16px`.
No sidebar, no dashboard grid, no metric tiles, no nav bar, no tabs.

Top to bottom, exactly as built:

1. `h1` "CageCheck" + one-line tagline (positioning).
2. Cage card (dashed border): what the cage does for every check.
3. Paste box: one `textarea` (the only input).
4. Four buttons: "Check in cage" (primary, ink) + three presets
   (attack / policy-toggle / clean).
5. Result: stamp + receipt slip + conditional approval action.
6. Small links: "Past receipts" · "Health (cage tier + Inference status)".
7. Past-receipts list area (populated only after clicking the link).

Note the divergence from the strategist draft: the cage card comes
**before** the paste box in the built UI, not after it.

## 7. Navigation and information architecture

There is no navigation. There is one screen (`GET /`). "Past receipts"
is a single text link that renders a list in place; "Health" is a plain
link to the JSON `GET /health` endpoint (it leaves the UI for raw JSON
and has no back link — see the interaction inventory). There is no
link in the UI to `GET /audit`; that route exists for API use only.

## 8. Component behaviour — as built

- **Paste box:** plain `textarea`, mono font, grey border, placeholder
  "Paste an AI-suggested Python snippet here…". No `<label>` element
  (accessibility gap — see §11).
- **Check in cage:** solid ink button. On click it `POST`s to
  `/api/check`. There is **no loading state, no progress bar, and no
  disabled state during the fetch** (the strategist draft's "Checking…"
  state was not implemented). Rapid double-clicks therefore send
  duplicate requests, each appending an audit entry.
- **Presets:** fill the textarea only; they do not run a check by
  themselves. Attack → secret-path BLOCKED. Policy-toggle → write
  outside the cage BLOCKED. Clean → PASSED with cage output `60`.
- **Stamp:** appears instantly via `innerHTML`. There is **no stamp
  animation** in the built CSS/JS (the strategist draft's 200ms
  scale-down animation was not implemented).
- **Receipt slip:** white, mono, `white-space: pre-wrap`,
  `word-break: break-word` — the full receipt JSON, escaped. There are
  **no "Copy receipt id" / "Copy full receipt" buttons** (strategist
  draft feature, not built).
- **Approve button:** rendered only when the stamp is not BLOCKED,
  labelled "Approve clean snippet for repo" with the note "Approval
  means cleared to copy, not sent anywhere. Nothing is sent." For a
  BLOCKED result there is no approval button at all, and the UI says
  so in words. **Defect:** the same "clean snippet" label is used for
  HELD results too, even though the server approves HELD as
  `approved_clean_or_held` — the label overstates cleanliness for HELD.
- **Past receipts:** renders `receipt_id · stamp · policy_rule ·
  detail` per row. Rows are **not clickable** to a full slip, even
  though `GET /receipts/<id>` exists (see inventory).
- **Error states:** an empty snippet or oversize snippet shows the
  server error as a paragraph (`Paste a snippet first`,
  `Snippet too large (64 KiB limit)`). Approve errors are appended as
  raw JSON with no distinct error styling (see inventory).

## 9. Motion language — as built: none

No CSS transitions, no keyframe animations, no hover animations that
change layout. The stamp simply appears. This is restrained, but it is
not the strategist draft's "one purposeful stamp animation" — that
animation does not exist in the built UI and must not be claimed.

## 10. 3D concept — PLANNED ONLY, NOT IMPLEMENTED

**Status: PLANNED. No 3D exists in the built UI. No exception has been
approved. Do not claim 3D is present.**

Proposed concept (to be designed properly before any implementation):

- **What it is:** a small, supplementary "cage view" beside (never
  instead of) the stamp + receipt. A transparent cage box rendered in
  CSS 3D (preferred first attempt — no new heavy dependency) or, only
  if CSS 3D proves insufficient, a lazily loaded WebGL scene. The
  snippet enters the cage as a labelled block; policy rules appear as
  cage bars; a blocked attempt (e.g. a secret-path read) visibly
  stops at a bar and produces the same stamp + receipt; a passed
  snippet exits the cage and receives its stamp.
- **Why it is meaningful:** it makes the containment boundary itself
  visible — the product's core claim is that the policy lives outside
  the cage, and a cage diagram shows inside vs. outside spatially in a
  way a bullet list does not.
- **What the user can manipulate:** rotate / inspect the cage (drag or
  keyboard arrows), click a bar to see the rule it represents
  (secret-path, network, subprocess, write-outside). Every interaction
  must also be available as text: the stamp + receipt remain the
  authoritative evidence, and the 3D view must never be the only place
  a decision is shown.
- **Loading / error / fallback:** lazy-loaded, never blocking the
  check workflow. If WebGL / CSS 3D is unavailable, or on a low-power
  device, fall back to the existing static 2D cage card + stamp +
  receipt, with no loss of function. On load failure, show the 2D
  fallback, not an error wall.
- **Mobile / performance:** a small, capped scene; no full-screen
  canvas; no auto-rotation by default.
- **Accessibility / reduced motion:** honour `prefers-reduced-motion`
  (no rotation, static cage view). Provide keyboard alternatives for
  every 3D interaction. The 3D view must be tested on a laptop and a
  mobile viewport before it is claimed — neither test exists yet.

Until this is implemented and tested, Gate C (3D) is FAIL and the
overall release is not COMPLETE.

## 11. Responsive and accessibility — honest status: UNTESTED / GAPS

- Viewport meta tag is present; single 720px column with
  `box-sizing: border-box` on the textarea is structurally
  narrow-friendly, but **there are no media queries and no
  tablet/mobile test evidence** (no viewport screenshots, no
  Lighthouse run).
- Keyboard: native `<button>` / `<textarea>` Tab order works by
  construction, but **no keyboard/focus test was run, and no custom
  focus-visible styles exist** (browser defaults only).
- Labels: the textarea has **no `<label>`**, placeholder only.
- Contrast: ink on paper is high-contrast by inspection, but **no
  contrast measurement was run** — do not claim a WCAG AA pass.
- Reduced motion: moot for the built UI (no motion), but the planned
  3D view must honour it (see §10).
- Result: responsive/accessibility is **FAIL** under the rulebook
  until viewport tests, a focus test, a label fix, and a contrast
  check are recorded.

## 12. Design research — BLOCKED for this gate pass

No new web design-reference inspection was performed for this gate
file, so **no reference is listed here as inspected**. Do not treat
the strategist pack's reference notes as this pass's inspection.

Prior work (not this pass's inspection): the strategist pack at
`~/workspace/hackathons/vultr-agent-rush/strategist/design/DESIGN_CONSTITUTION.md`
(3 Nov 2026) contains reference notes for GOV.UK's design system,
Stripe's dashboard/docs, and GitHub's security UI, with its own
disclaimer that those references were not claimed as inspected in
full. That file was **not copied verbatim** into this constitution;
this file was written from the actual built UI.

Distinctness comparison (from the strategist pack's prior-project
notes, not fresh inspection): CageCheck's paper/stamp single column is
recognisably different from the three most recent prior identities
noted there — ChatBoss's dark gradient game overlay, Abhiverse's
Windows-XP neo-retro, and the 2 Nov Containment Receipt Agent's
multi-panel dashboard. No purple gradient, glass card, sidebar, or
metric-tile template is reused. On that comparison, UI distinctiveness
is PASS; the research-reference sub-item of Gate A remains incomplete
until five references are actually inspected and recorded.

## 13. Original design decisions (built UI)

- One screen, one input, one primary action — deliberately less than
  a dashboard, so a judge sees the containment moment in one scroll.
- Paper/ink/stamp instead of dark/game/retro: a security decision
  should look like a stamped decision, not a game or a nostalgia piece.
- Receipt as JSON slip, not a toast: a block must be quotable back
  (receipt_id, rule, replay instruction).
- No CDN, no webfonts, no external assets: the page renders from one
  HTML file served by the stdlib server.
