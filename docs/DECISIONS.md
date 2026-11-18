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

### Exact-repeat investigation results — 2026-11-17

Recorded from executed cells in `notebooks/03_duplicate_investigation.ipynb` (training period only):

- The 49,157 training rows contain 3,472 exact repeated row patterns covering 19,763 rows. There are 16,291 later occurrences beyond each pattern's first row; the largest exact pattern appears 150 times.
- The repeated-group rows include 11,383 canceled bookings, 8,217 check-outs, and 163 no-shows. Matching fields include the outcome/status columns, but that does not prove the repeated rows are invalid exports.
- A **hypothetical** collapse of exact repeats would leave 32,866 training rows, lower the train cancellation rate from 35.77% to 22.17%, and reduce booking counts on 657 hotel-arrival nights.
- No booking identifier is present to establish a correct deduplication key. The source and current working data remain unchanged. The Step 1 choice to retain or disapprove remains the user's decision.

## Frozen choice before the proof run (2026-11-18)

Recorded **before** any proof (test) file was opened, at the user's instruction to run the chosen model on test. Settings are in `models/frozen_choice.json` (with file fingerprints of the model and preprocessor); reasoning in `notebooks/13_validation_results_explained.ipynb`.

| Setting | Frozen value | Chosen how |
|---|---|---|
| Method | CatBoost, fitted on train only (`notebooks/11_train_models.ipynb`), on the inputs prepared in `notebooks/10_preprocessing_leakage_checked.ipynb` | Lowest choose-period cost under the walk ceiling, under both buffer structures |
| Rule | k = max(0, floor(expected cancellations) − buffer) | Same rule for every method |
| Buffers (primary) | City Hotel 6, Resort Hotel 3 | Cheapest per-hotel pair meeting the group-wide ceiling on choose |
| Flat-rule benchmark | Train hotel rates (City 41.7%, Resort 25.2%); buffers City 20, Resort 4 | Same selection, same ceiling |
| Secondary (disclosed) | Shared buffer: CatBoost 5, flat rule 16 | Reported for transparency; flatters the model (notebook 13, Part 5) |

Choose-period evidence: CatBoost −1.4% vs the flat rule with per-hotel buffers, cheaper in 74% of week resamples, 3 of 6 months; **not a reliable difference**. Four inputs remain provisional (timing unverified). Any change after seeing proof results must be disclosed and both runs reported (`docs/EVALUATION_CONTRACT.md`).

## Proof run 1 result (2026-11-18)

`notebooks/14_test_run.ipynb`, frozen settings above. CatBoost cost **EUR 3,365,371** against **EUR 3,214,912** for the flat rule with per-hotel buffers: **EUR 150,459 more (−4.7%), no saving**. Empty rooms 7,322 vs 7,166; walked guests 210 vs 179; walks per 1,000 arrivals 8.42 vs 7.18 — **group guardrail met by both**. By hotel: City Hotel CatBoost EUR 18,259 cheaper; Resort Hotel EUR 168,718 dearer (walks per 1,000: Resort 10.30 vs 11.29, no per-hotel threshold). Test accuracy at a 50% cut-off 63.5% (61.3% for "nobody cancels"), ROC AUC 0.679; predicted cancellation rate 27.2% vs actual 38.7%. Secondary shared-buffer comparison (disclosed beforehand as flattering the model): CatBoost EUR 431,799 cheaper (11.0%).

## Post-proof change: run 2 with XGBoost (2026-11-18) — must be disclosed

At the user's instruction, **after seeing run 1**, the method is changed from CatBoost to **XGBoost**, with its choose-period buffers from notebook 13 unchanged (per hotel: City 6, Resort 3; shared: 5) and the same flat-rule benchmark. Settings: `models/frozen_choice_run2_xgboost.json`. Because this choice was made after test results were seen, run 2 is **test-informed**: both runs must be reported (slide 5, `docs/EVALUATION_CONTRACT.md`), and run 2 cannot be presented as a clean proof result on its own.

## Run 2 superseded; run 3 planned: refit on train + choose (2026-11-18) — must be disclosed

Run 2 (XGBoost, train-only fit) was frozen in `models/frozen_choice_run2_xgboost.json` but **never executed**: at the user's instruction it is replaced by run 3. Run 3 refits the preprocessor (same settings) and **both CatBoost and XGBoost** (same settings as notebook 11) on **train + choose**, which `docs/EVALUATION_CONTRACT.md` allows provided every setting picked on choose is kept: the rule, the buffers (per hotel City 6 / Resort 3 for both models; shared 5), and the flat rule with its **train** rates and buffers (City 20 / Resort 4; shared 16). Declared before the run: **CatBoost is primary** (the method chosen on choose, notebook 13); XGBoost is reported alongside and will not be selected on test results. A flat rule using train + choose rates is reported as a disclosed fairness check. Run 3 follows run 1's test results, so **all runs are reported** (slide 5). Notebooks: `notebooks/15_retrain_train_val.ipynb`, `notebooks/16_final_test_run.ipynb`.

## Proof run 3 result (2026-11-18) — test-informed, reported with run 1

`notebooks/16_final_test_run.ipynb`, settings frozen in `models/frozen_choice_run3_train_val.json` (notebook 15) before test was opened. Benchmark identical to run 1 (flat rule, train rates, per-hotel buffers City 20 / Resort 4): EUR 3,214,912; 7,166 empty rooms; 179 walks; 7.18 walks per 1,000 — guardrail met.

| Run | Method | Cost (EUR) | Empty rooms | Walked guests | Walks per 1,000 | Guardrail | vs flat rule |
|---|---|---:|---:|---:|---:|---|---:|
| 1 (frozen before any test result) | CatBoost, train fit | 3,365,371 | 7,322 | 210 | 8.42 | met | −150,459 |
| 2 | XGBoost, train fit | — | — | — | — | not run (superseded) | — |
| 3, primary (after run 1) | CatBoost, train + choose fit | 2,804,174 | 5,889 | 327 | 13.11 | **BREACHED** | +410,738 |
| 3, also reported | XGBoost, train + choose fit | 2,799,388 | 5,883 | 326 | 13.07 | **BREACHED** | +415,524 |

Under `docs/EVALUATION_CONTRACT.md` a rule that saves euros but breaks the ceiling is **rejected**: run 3 is not acceptable. Cause: the refitted models expect more cancellations (notebook 15, Step 5: about +5 rooms per City Hotel night) while the buffers stay at the values chosen for the train-only models, so they oversell more. Re-choosing the buffers on proof results is not permitted. No model run is both cheaper than the flat rule and within the ceiling on proof.

## Pipeline 05–14 (`notebooks/pipeline/`): decisions and freeze, recorded before its Proof run (2026-11-18)

**Historical disclosure:** the Proof period was already inspected in the earlier runs above. This pipeline's Proof evaluation (notebook 12) is therefore **retrospective, not historically blind**, and is reported as such.

| # | Decision | Reason | Where |
|---|---|---|---|
| P1 | Notebooks 05–14 copied from the 2026-11-15 working set into `notebooks/pipeline/`; `src/features.py`, `src/nightly.py`, `tests/test_nightly.py`, `models/xgboost*`, `models/conformal_quantiles.json`, `evidence/expanded_benchmark/`, `outputs/nightly_recommendations*` copied from the uncommitted files in `IIT_GN_W06_submission_working.zip` | They existed only outside the repository; hashes in `evidence/pipeline_run/provenance.json` | — |
| P2 | Each notebook starts by moving to the repository root | They import `src` and write relative `evidence/` paths | first code cell |
| P3 | Approved inputs: `hotel`, `market_segment`, `distribution_channel`, `agent`, `company`, `is_repeated_guest`, `previous_cancellations`, `previous_bookings_not_canceled`; **`country` excluded** (correct nationality often known only at check-in) | Notebook 05 decision; four inputs remain provisional on timing | 05 |
| P4 | Notebooks 09–12 read earlier selections from files instead of hand-copied placeholders (`logistic_regression, C=1.0`, `model_buffer_1.0`) | Notebook 08 actually selected **logistic regression C = 0.1** (mean chronological Brier 0.1731); the placeholders would have evaluated an unselected model | 09–12 |
| P5 | Calibration rule fixed before 09 ran: adopt only if Choose Brier **and** log loss both improve. Result: **adopted** (Brier 0.2091 → 0.2011; log loss 0.6105 → 0.5857). Improves City Hotel Brier (0.2172 → 0.2053), slightly worsens Resort (0.1915 → 0.1919) | Pre-declared rule | 09, `evidence/probability_calibration/calibration_decision.json` |
| P6 | Policy candidates in 11 = the brief's declared set **plus** two declared families: the contract's flat rule `max(0, ceil(hotel rate × bookings) − m)` and the model with the same margin `max(0, ceil(E) − m)`, m = 0…60. Uncalibrated model policies reported as reference only | `docs/EVALUATION_CONTRACT.md` defines the flat rule with a margin chosen on choose; rule 5; the declared buffers only add rooms | 11 |
| P7 | Selection: drop policies above 10 walks per 1,000 on Choose, take the lowest cost | Brief and contract | 11 |

**Choose result (notebook 11):** every declared model policy breaches the ceiling (72–173 walks per 1,000). Meeting the ceiling: flat rule margin 17 (EUR 2,414,409; 5,532 empty rooms; 169 walks; 9.06 per 1,000), model (calibrated LR) margin 18 (EUR 2,576,784; 9.76 per 1,000), no overbooking (EUR 4,155,341).

**Frozen before notebook 12 ran** (`evidence/choose_policy_selection/frozen_configuration.json`, 2026-11-18T02:32:44): selected policy **flat rule, margin 17** (train hotel rates City 41.7%, Resort 25.2%; ceil rounding). Declared Proof benchmarks: the same flat rule, and the best model policy on Choose (calibrated logistic regression C = 0.1, margin 18). Notebook 12 checks the 08/09 evidence fingerprints against the freeze before scoring.

## Pipeline 05–14: results and reconciliation, recorded after its Proof run (2026-11-18)

**Proof (notebook 12, retrospective; nothing changed after scoring):** frozen flat rule, margin 17: **EUR 3,935,876; 8,186 empty rooms; 155 walks; 6.21 per 1,000 — group ceiling met.** City Hotel 9.23 per 1,000, Resort Hotel 0.99 (no per-hotel threshold given). Declared model benchmark (calibrated logistic regression C = 0.1, margin 18): EUR 4,172,660; 277 walks; **11.11 per 1,000 — ceiling breached**; EUR 236,784 more than the flat rule. Evidence: `evidence/proof_evaluation/`.

| # | Decision | Reason | Evidence |
|---|---|---|---|
| P8 | `src/features.py` now implements the approved feature set (P3): `country` removed and listed in `HELD_BACK`; `tests/test_features.py` fails if a held-back or post-outcome field returns | Notebook 05 required the code to match its decision and a guarding test | `tests/test_features.py` |
| P9 | `src/nightly.py` validates a saved model against `features.CATEGORICAL`/`NUMERIC` instead of its own hard-coded list (which included `country`) | One schema source; a stale artifact now fails loudly instead of running | notebook 14 |
| P10 | `models/xgboost.joblib` is **not** reconciled: it was trained with `country` and is rejected by the nightly pipeline. It was not retrained here | Retraining it would also need its conformal state and policy reconciled with the policy actually selected (the flat rule); left as a blocker | `evidence/nightly_pipeline_validation/` |
| P11 | `evidence/expanded_benchmark/` is treated as **not comparable** with this pipeline: it used `country`, its source code (`src/run_cv_benchmark.py`, `src/mlops_tracking.py`) is absent, and its Proof rows were already exposed | Cannot be reproduced or audited | notebook 13 |

`src/contract.py` is unchanged: its SHA-256 differs from the benchmark's record only because this checkout stores CRLF line endings (LF-normalised hash matches `7be10099…`).

## Nightly command rewired to the frozen run-1 choice (2026-11-18)

- **Change:** `src/nightly.py` no longer loads `models/xgboost.joblib`. That model was trained with `country` and was rejected by the schema check. The command now reads `models/frozen_choice.json` and refuses to run unless the CatBoost and preprocessor files match their SHA-256 fingerprints.
- **Output:** for each hotel-night it prints the recommended flat rule (Train hotel rates, buffers City 20 / Resort 4), with the frozen CatBoost (buffers 6 / 3) alongside. Both use `max(0, floor(expected) - buffer)`.
- **What it does not do:** it never fits anything and never reads `is_canceled`. It is a historical replay on final-book data, not a live forecast (project rule 7).
- **What did not change:** no choice changed. The frozen files, buffers and recommendation are as recorded before the test, and the old XGBoost and conformal files are left in `models/`, unused.
- **Verification:** `tests/test_nightly.py` checks that the command's expected counts for 18–31 Aug 2017 equal notebook 14's saved predictions. It also checks that a changed model file is refused. 12 tests pass.
