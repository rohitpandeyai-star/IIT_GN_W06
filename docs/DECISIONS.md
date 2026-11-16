# Data Decisions and Team Objections

> **AI-assisted working log.** This pass documents the current initial profile and conservative feature-timing choices. Add a dated row for each later cleaning, filtering, or feature decision; do not silently rewrite earlier decisions.

## Data decisions

| Date | Decision | Reason / evidence | Rows touched | Logged by |
|---|---|---|---:|---|
| 2026-11-17 | Keep the raw booking rows unchanged in the initial profile; no rows were removed or deduplicated and no values were recoded. | Initial profile covers 119,390 rows and 32 columns. No cleaning operation was performed in the current notebooks. | 0 changed; 119,390 reviewed | Rohit Pandey, Data Lead |
| 2026-11-17 | Use the arrival-date split from `src/contract.py`: train 49,157, choose 29,546, proof 40,687. | This preserves the required time order; early notebook outcomes were summarized only for train/choose. | 0 removed; all 119,390 assigned to a period | Rohit Pandey, Data Lead |
| 2026-11-17 | Hold proof cancellation outcomes out of the early profile and tuning. | Proof is for one final evaluation after settings are frozen. Existing early checks calculated only proof counts/dates, not proof cancellation rate. | 0 removed; 40,687 proof rows held for later scoring | Rohit Pandey, Data Lead |
| 2026-11-17 | Keep City Hotel and Resort Hotel separate in summaries and later candidate reports. | Dataset has two distinct hotel values. Train+choose cancellation rates differ: City 41.3%, Resort 26.3%. The same supplied contract applies, but no evidence establishes identical operating rules. | 0 removed; all 119,390 retained | Rohit Pandey, Data Lead |
| 2026-11-17 | Do not treat `agent` or `company`'s source `NULL` category as a missing-value error or recode it in this pass. | Dataset article says NULL in these categories means not applicable (for example, no travel agent). No recoding was performed. | 0 changed | Rohit Pandey, Data Lead |
| 2026-11-17 | Exclude bin 2 and bin 3 columns from the selected MVP predictors until point-in-time availability is verified; reserve `is_canceled` as the target only. | The dataset article describes extraction from booking records/change logs as of the day before arrival, not a full original-booking snapshot. `booking_changes`, country, status, and status date can reveal later events. See `docs/COLUMNS.md`. | 0 rows removed; predictor restriction applies to future model inputs | Rohit Pandey, Data Lead |

### Different hotel groups / decision rules

The data identifies two properties as City Hotel and Resort Hotel, with different train+choose cancellation rates. This supports separate reporting and retaining `hotel` as a grouping field. The brief and evaluation contract do not provide separate rules or thresholds by hotel; the current shared walk ceiling is 10 per 1,000 arrivals. Do not infer different capacity, cancellation policy, or customer rules from the rate difference alone. Ask the client whether it needs an additional per-hotel guardrail.

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
