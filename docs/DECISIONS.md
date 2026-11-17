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
| PRD method comparison | Compare a hotel-by-history lookup, logistic regression, a depth-limited decision tree (maximum depth 3), Random Forest, XGBoost, and CatBoost, all against the flat-rule baseline. Prefer the lookup if the more complex candidates do not lower choose-period cost while meeting the same ceiling. | The PRD defines a low-complexity fallback and two distinct learned candidates; no results exist yet. | Candidate plan; final method awaits Step 5 choose-period evidence. |
| PRD inputs | Restrict candidate predictors to the learner's current Bin 1 fields (`hotel`, `is_repeated_guest`, `previous_cancellations`, `previous_bookings_not_canceled`); use `is_canceled` as target only. | `docs/COLUMNS_USER_REVIEW.md`; source timing still needs point-in-time verification for operational use. | Proposed; review with feature audit in Step 5. |
| PRD segmentation | Set segmentation outputs to zero in MVP. Reopen only if the client identifies an action and the segmented candidate improves choose-period cost by at least 5% while meeting the walk ceiling. | No action or measurable value for hidden guest types is stated in the brief. The 5% is a proposed internal gate, not a client threshold. | Proposed; client confirmation required before treating it as a requirement. |
| Build plan | Budget 18 hours for POC/data preparation, 8 for MVP, and 4 for final evidence/roadmap; record actual time separately. | Initial planning estimate for one person assigned all roles; production estimates are discovery-dependent. | Planning estimate; revise as work is done. |
| Evaluation discipline | Select all settings on choose data, compare candidates on the same hotel-nights, keep proof outcomes unseen until freeze, then run proof once. | Required by `docs/EVALUATION_CONTRACT.md`; prevents tuning against proof. | Required procedure. |

## Step 5 data-preparation order (2026-11-17)

> Planning note at the user's correction: the project has not completed full EDA, cleaning, final feature selection, feature engineering, or a modeling-preparation split. The notebooks contain brief-number checks and the contract arrival-date period definitions; those are not the full modeling workflow. `src/features.py` is not present yet.

1. Read the raw file unchanged and inspect its schema/quality (shape, types, missing/sentinel values, duplicates, ranges, and categories) without target-driven cleaning decisions.
2. Create train, choose, and proof partitions with `src/contract.py` by arrival date. The periods exist; implement and document their use in the modeling pipeline. Do not substitute a random split.
3. Run target/feature EDA on train. Use choose only for the planned method and buffer comparisons; keep proof outcomes out of EDA, cleaning, feature selection, and tuning until freeze.
4. For each cleaning or retention choice, record the evidence and the number of values/rows affected. Leave raw values unchanged unless a documented reason supports a transformation.
5. Treat the learner's Bin 1 fields as a provisional feature pool, not a final engineered set. Verify timing, choose the usable features, and fit any encoders/imputers/derived transformations on train only; apply the fixed transformations to choose and proof.
6. Only after these checks compare the flat rule, lookup, logistic regression, shallow tree, Random Forest, XGBoost, and CatBoost if runtime permits. Select method and buffer on choose under the walk ceiling, freeze, then evaluate proof once.

The initial notebook run completed the split, train-period profile, retain-raw decision, and provisional feature matrices for steps 1–5. No row/value cleaning was applied. Final feature/timing approval and all model comparisons remain pending.

### Split execution record — 2026-11-17

`notebooks/02_natural_language_data_prep.ipynb` loaded the source unchanged and assigned all 119,390 rows using `contract.split_periods()`: train 49,157 rows (2015-07-01–2016-06-30), choose 29,546 (2016-07-01–2016-12-31), proof 40,687 (2017-01-01–2017-08-31). The notebook displayed only counts, dates, and hotel names for proof; it did not compute proof cancellation outcomes. No CSV partitions were written and no cleaning was performed.

### Initial data-preparation results — 2026-11-17

Recorded from executed cells in `notebooks/02_natural_language_data_prep.ipynb`; the profile covers all 32 source columns on train:

| Check | Result | Decision |
|---|---|---|
| Training dimensions | 49,157 rows x 33 columns including derived `arrival_date` | Use the contract split; source itself has 119,390 rows x 32 columns. |
| Exact repeated rows in train | 16,291 duplicate occurrences after the first matching row | Keep them. There is no reservation ID in these columns to prove they are erroneous bookings. |
| Missing values in train | `company` 46,123; `agent` 6,960; `country` 284; `children` 4 | Do not fill these fields in this step; they are outside the provisional feature pool. |
| Candidate feature missingness | Zero missing in train, choose, and proof for `hotel`, `is_repeated_guest`, `previous_cancellations`, and `previous_bookings_not_canceled` | No imputation is needed for the current candidate set. Proof target values were not used. |
| Training target | 17,585 cancellations of 49,157 bookings (35.8%); City Hotel 41.7%, Resort Hotel 25.2%. Across the 12 training months, City Hotel rates ranged 24.4%–67.2% and Resort Hotel 13.5%–34.8%. | Descriptive train-only profile; highlights variation, not a model result or proof of a stable seasonal rule. |
| Checked numeric ranges | No negative values in adults, children, babies, stay nights, ADR, or prior-booking counts; maxima include 55 adults and ADR 5,400 | Preserve unusual non-negative values pending schema/client evidence; do not clip based on magnitude alone. |
| Raw cleaning | Zero rows removed; zero values recoded or clipped | Keep raw table unchanged. |
| Provisional feature matrices | Seven features: repeated-guest flag, two prior counts, their `log1p` versions, and two hotel one-hot columns. Shapes: train 49,157 x 7; choose 29,546 x 7; proof 40,687 x 7. No missing feature values. | Feature transforms are for candidate evaluation only; source timing still needs verification. No proof outcomes were examined. |

The train profile also records each source column's type, missingness, distinct count, and three most common values, plus numeric minimum/median/99th percentile/maximum and negative count. `is_canceled`, `reservation_status`, and `reservation_status_date` are excluded from predictors because they are the target or post-outcome fields. Prior-count zeros are common (43,348/49,157 for previous cancellations; 47,813/49,157 for previous non-cancelled bookings), motivating the provisional `log1p` features.

These are descriptive checks and a provisional feature preparation. No model has been fit, no method/buffer selected, and no proof cancellation metric calculated.

### User approval gates — pending (2026-11-17)

`notebooks/02_natural_language_data_prep.ipynb` now presents each observation and proposed action separately. No cleaning or feature proposal is treated as approved. Pending gates are: retain exact repeated rows; leave non-candidate missing values unchanged; retain unusual non-negative values; use the four Bin 1 fields provisionally; include or omit `log1p` count features; and use train-derived one-hot hotel indicators. The period split was directly requested and is complete. Final feature matrices remain blocked until required gates are approved; a disapproved required gate pauses work for discussion.
