# Data Decisions and Team Objections

> **AI-assisted preliminary log.** The data entries below distinguish observed handling from proposed choices. The learner's 32 current column bins and reasons are recorded in `docs/COLUMNS_USER_REVIEW.md`; their point-in-time accuracy has not been independently verified. New planning items below are assistant proposals at the user's direction, not client-confirmed facts. Add dated entries for later cleaning, filtering, model, or feature decisions; do not silently rewrite earlier decisions.

## Data decisions

| Date | Observed handling or proposed choice (pending learner review) | Evidence / reason to consider | Rows touched | Status |
|---|---|---|---:|---|
| 2026-11-17 | Initial profile left raw rows and values unchanged; no rows were removed, deduplicated, or recoded. | Existing profile covers 119,390 rows and 32 columns; no cleaning operation was recorded. | 0 changed; 119,390 reviewed | Observed fact; learner review pending |
| 2026-11-17 | The contract uses arrival-date train/choose/proof splits: 49,157 / 29,546 / 40,687 bookings. | Existing notebook profile reports these counts; contract defines the periods. | 0 removed; all 119,390 assigned to a period | Observed fact; learner review pending |
| 2026-11-17 | Earlier profile held proof cancellation outcomes out of its summary. | Proof is for one final evaluation after choices freeze; existing early checks reported proof count/date only. | 0 removed; 40,687 proof rows reserved | Prior procedure; learner review pending |
| 2026-11-17 | Suggested separate City Hotel and Resort Hotel reporting. | Two hotel values; train+choose cancellation rates are 41.3% and 26.3%. This does not prove different operating rules. | 0 removed; all 119,390 retained | AI suggestion; learner decision pending |
| 2026-11-17 | Existing notes say not to recode the `NULL` category for `agent` or `company`. | Dataset article describes these `NULL` values as not applicable, such as no travel agent. No recoding was performed in the initial profile. | 0 changed | AI suggestion based on source; learner review pending |
| 2026-11-17 | Earlier AI audit suggested excluding uncertain/late columns from model predictors until point-in-time availability is verified, and using `is_canceled` only as the target. | Source article describes values captured from booking/change logs as of the day before arrival. See the learner's sequential notebook and `docs/COLUMNS.md`. | 0 rows removed; provisional predictor recommendation only | AI suggestion; learner decision pending |

### Different hotel groups / decision rules

The data identifies two properties as City Hotel and Resort Hotel, with different train+choose cancellation rates. The assistant proposed separate reporting and retaining `hotel` as a grouping field. Decide whether you agree. The brief and evaluation contract do not provide separate rules or thresholds by hotel; the shared walk ceiling is 10 per 1,000 arrivals. A rate difference alone does not prove different capacity, cancellation policy, or customer rules.

## Team decisions and objections

| Date | Artifact | Decision or objection | Raised by | Answer, within 15 minutes | Settled by |
|---|---|---|---|---|---|
| 2026-11-17 | Charter / RFP | Proceed with AI-assisted framing and explicitly label it; the course's AI-free paper-frame requirement is not met by this draft. | User / Client Lead | Keep the distinction visible in the charter, paper-frame draft, and tracker; proceed with the user's requested sequence without claiming course compliance. | User direction recorded; Rohit Pandey |
| 2026-11-17 | Column audit | Do not treat the day-before-arrival extract as proof of values fixed at original booking time. | Data Lead | Use conservative timing bins; exclude uncertain and post-outcome variables from selected MVP predictors until point-in-time snapshots are verified. | Rohit Pandey |

## Pending decisions

- Exact safety margin in the client's flat rule and whether it differs by hotel.
- Whether the client wants a per-hotel walk ceiling in addition to the scored group-wide ceiling.
- Minimum savings threshold, if the client expects one beyond improving on the flat-rule baseline.
- Whether a real morning run must use the reservations present at that run time rather than the full final book used by the exercise.
- Which amendable fields can be reconstructed at the intended prediction timestamp.

## Step 4 planning proposals (2026-11-17)

| Artifact | AI-assisted proposal | Evidence / reason | Status |
|---|---|---|---|
| PRD method comparison | Compare a hotel-by-history lookup, logistic regression, and a depth-limited decision tree (maximum depth 3), all against the flat-rule baseline. Prefer the lookup if the more complex candidates do not lower choose-period cost while meeting the same ceiling. | The PRD defines a low-complexity fallback and two distinct learned candidates; no results exist yet. | Candidate plan; final method awaits Step 5 choose-period evidence. |
| PRD inputs | Restrict candidate predictors to the learner's current Bin 1 fields (`hotel`, `is_repeated_guest`, `previous_cancellations`, `previous_bookings_not_canceled`); use `is_canceled` as target only. | `docs/COLUMNS_USER_REVIEW.md`; source timing still needs point-in-time verification for operational use. | Proposed; review with feature audit in Step 5. |
| PRD segmentation | Set segmentation outputs to zero in MVP. Reopen only if the client identifies an action and the segmented candidate improves choose-period cost by at least 5% while meeting the walk ceiling. | No action or measurable value for hidden guest types is stated in the brief. The 5% is a proposed internal gate, not a client threshold. | Proposed; client confirmation required before treating it as a requirement. |
| Build plan | Budget 12 hours for POC, 8 for MVP, and 4 for final evidence/roadmap; record actual time separately. | Initial planning estimate for one person assigned all roles; production estimates are discovery-dependent. | Planning estimate; revise as work is done. |
| Evaluation discipline | Select all settings on choose data, compare candidates on the same hotel-nights, keep proof outcomes unseen until freeze, then run proof once. | Required by `docs/EVALUATION_CONTRACT.md`; prevents tuning against proof. | Required procedure. |
