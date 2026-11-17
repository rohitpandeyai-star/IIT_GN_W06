# Charter and RFP Grill 1 — compressed AI-assisted record

**Owner:** Client Lead (Rohit Pandey, assigned by the user)
**Date:** 2026-11-17
**Tool:** Codex AI assistant
**Session record:** `ai_logs/20261117_client-lead_codex_grill-charter.md`

> The user asked to answer the grill questions in one pass because they had no time. All responses below are AI-assisted proposals made at the user's direction. They are not presented as the user's own words or as client-confirmed facts. This compressed exchange does not claim to satisfy the course's 45-minute format.

| Q | Question asked | AI-assisted proposed response | Disposition | Document change |
|---|---|---|---|---|
| 1 | What exact safety margin does the current flat rule use, and does it vary by hotel or season? | The brief does not specify it. Keep the baseline margin unknown; do not choose a number and call it the client's rule. Ask for the current formula and its hotel/season variation. | Applied provisionally; client confirmation remains open. | `docs/CHARTER.md` and `docs/RFP.md`: added an explicit no-invention gate for the baseline margin. |
| 2 | Does the 10-walks-per-1,000-arrivals ceiling apply to the group, each hotel, or both? | The supplied contract defines a group-wide scored ceiling. Report both hotels separately as diagnostics, but do not claim each hotel meets an independent ceiling unless the client sets one. | Applied provisionally; request per-hotel requirement. | `docs/CHARTER.md` and `docs/RFP.md`: separate the contractual group guardrail from per-hotel reporting. |
| 3 | Who approves the rule, bears a walk's cost, and can override a recommendation? | The brief names the revenue manager as decision user; final approver, cost owner, and override process are unconfirmed. Keep manual approval in the MVP and do not imply autonomous deployment. | Applied provisionally; client confirmation remains open. | `docs/RFP.md`: added approval/override as a pre-deployment confirmation item. |
| 4 | Is the morning table based on the full final book or only reservations known when the morning run occurs? | The course contract scores each arrival night's final book. A real morning run needs a timestamped reservation snapshot. Treat the current exercise as retrospective/full-book and do not call it a live morning forecast. | Applied. | `docs/CHARTER.md` and `docs/RFP.md`: state the full-book exercise limitation and snapshot requirement. |
| 5 | What evidence supports the vendor's “95% accuracy” claim? | No metric, dates, test population, or baseline are supplied. Treat it as an unverified anecdote; request those details and do not use 95% as an acceptance target. | Applied. | `docs/RFP.md`: require definition and evidence before comparison; no accuracy-only acceptance. |
| 6 | Are cancellations and no-shows operationally interchangeable for this decision? | The supplied target/scoring setup is the exercise definition. The client's operational treatment is unknown; ask whether a no-show has the same cost and action as a cancellation before deployment. | Applied provisionally; client confirmation remains open. | `docs/CHARTER.md`: preserve the target definition while making the operational distinction an open question. |
| 7 | How should we reconcile “about one in four” cancellations with the checked 36.2% train-plus-choose rate? | Keep both figures with their scopes. The dataset rate does not invalidate the brief's rough observation; ask which dates, population, and cancellation definition produced the client's estimate. | Applied. | `docs/RFP.md`: retain the discrepancy and add a period/definition reconciliation gate. |
| 8 | Should “hidden guest types” enter this MVP? | Not until the client specifies what decision a segment changes and how value will be measured. Keep segmentation outside the MVP for now. | Applied provisionally. | `docs/RFP.md`: retain as out of scope pending a measurable client use. |
| 9 | Does this AI-assisted material satisfy the course's AI-free paper-frame requirement? | No. The existing drafts disclose AI assistance; keep that status explicit and do not represent them as the student's AI-free V0. | Applied. | `docs/CHARTER.md`: reaffirmed in the status note; no compliance claim added. |

## What did we learn from this grill?

The hardest issue is that the client brief leaves the safety margin and operating authority undefined. That means a numerical baseline or live approval workflow cannot be inferred from the historical file. Until the client confirms those items, the work will label assumptions, keep the current rule reproducible only when its true margin is supplied, and present recommendations for human review.

## Session limits and follow-up

This was a compressed grill at the user's request, not a 45-minute session. The required screenshot demonstrating an assistant assumption or pushback was not captured in this environment. Step 3 remains in progress until the course-format evidence is supplied or the course owner waives it.
