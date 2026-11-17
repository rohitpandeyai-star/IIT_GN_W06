# Product Requirements Document: Cancellation-Aware Overbooking

> **Status: AI-assisted working draft, prepared at the user's request.** The method and buffer are not selected from measured results yet. Client-only details remain open questions. This is not a claim that the AI-free paper frame requirement has been met.

**Owner:** Build Lead — Rohit Pandey (assigned to all roles by the user)
**Purpose:** Specify the decision, candidate approaches, inputs, output, evaluation, limitations, and production boundary before implementation.

## 1. Who uses it, when, and what do they do with it?

The revenue manager is the intended decision user. For each hotel and arrival night, the tool recommends a non-negative whole-number oversell count, `k`. The manager reviews the recommendation and supporting counts; this MVP does not change reservations automatically.

The course exercise evaluates each night's **final book**. Its 14-night table is therefore a historical/replay exercise using the supplied data, not a live forecast from reservations available on a real morning. A production morning run would need timestamped reservation snapshots and a validated decision-time feature set. The client has not confirmed the live operating time, final approver, or override process.

## 2. Which approaches could decide, what are their tradeoffs, what do we choose, and what would change our choice?

The flat rule is the required benchmark in both comparisons. The candidate set for Step 5 is:

| Candidate | How it works | Advantages | Costs and risks |
|---|---|---|---|
| Hotel-by-guest-history lookup | Estimate cancellation rates from the training period for groups formed from `hotel` and the audited booking-history fields. Sum booking-level rates by hotel-night. | Easy to explain and audit; simple fallback if model results are close. | Small groups may have noisy rates; needs a fallback for unseen or sparse groups; less able to combine several signals. |
| Logistic regression | Estimate each booking's cancellation probability from the same approved first-bin inputs; sum probabilities by hotel-night. | Compact, interpretable probability model; combines signals without hand-written group rules. | Needs calibration and time-split evaluation; may not improve cost or walks; still depends on correct point-in-time feature availability. |
| Shallow decision tree (maximum depth 3) | Split bookings into a small number of groups using the same approved inputs, estimate each group's cancellation rate, and sum by hotel-night. | Can capture simple interactions while keeping the paths inspectable. | A small tree can still overfit; group rates need support checks; depth and any pruning must be set without proof data. |
| Random Forest | Average predictions from many bootstrapped decision trees. | Nonlinear benchmark with less dependence on one tree. | May be less calibrated or interpretable; tuning and feature importance do not establish causality. |
| XGBoost | Gradient-boosted trees trained sequentially to improve errors. | Strong tabular-data candidate; supports interactions. | Requires careful tuning and probability calibration; may overfit the choose period. |
| CatBoost | Gradient-boosted trees with support for categorical features. | Candidate for mixed categorical and numeric fields such as hotel plus booking-history counts. | More complex than the lookup or logistic baseline; compare fairly on identical inputs and periods. |

**Provisional implementation choice:** compare the lookup with logistic regression, a depth-limited decision tree, Random Forest, XGBoost, and CatBoost in Step 5, alongside the required flat-rule baseline. Use the same approved input set and arrival-date periods for every candidate; if runtime is constrained, record which candidates were omitted and why. Do not claim a final method now. Prefer the lookup if the candidates are indistinguishable on the choose period; choose a more complex model only if it has lower choose-period cost than the lookup and meets the walk ceiling. In every case, reject a candidate that exceeds the ceiling. Freeze the chosen method and buffer before proof.

The buffer converts the expected cancellation count into the integer `k`. Choose its value on the choose period by minimizing contract cost subject to no more than 10 walks per 1,000 arrivals; apply the same selection process to the flat-rule safety margin. If no candidate satisfies the ceiling, report that and do not present it as acceptable. Do not adjust settings after looking at proof outcomes; if a post-proof change is made, disclose both runs as the evaluation contract requires.

## 3. What is our answer to the wish-list item?

**MVP scope: zero guest-segmentation outputs.** “Hidden guest types” do not change a defined action in the current brief, so they are excluded from the deliverable. As a proposed internal re-entry test (not a client requirement), revisit segmentation only if the client names an action it would change and a segment-based candidate reduces choose-period cost by at least 5% versus the selected non-segmented candidate while meeting the same walk ceiling. A segment that changes no recommendation or fails that test adds no demonstrated value.

## 4. What exactly is in the table the client reads?

One row per hotel and arrival night for the requested 14-night window, with:

- `hotel` and `arrival_date`;
- number of bookings in the scored book;
- expected cancellations (sum of booking-level probabilities, or the lookup estimate);
- selected buffer in rooms;
- recommended whole-number oversell count `k`;
- method name and a short reason showing how the count was derived.

The evaluation report also shows empty rooms, walked guests, walks per 1,000 arrivals, and total cost in euros, for the chosen method and flat-rule baseline, across the proof period. Show hotel-level results as diagnostics, while applying the supplied group-wide walk ceiling unless the client confirms separate per-hotel ceilings.

For the course command `python src/nightly.py --from 2017-08-18 --nights 14`, identify the result as a historical replay on the supplied dataset. It must not be described as an actual future 14-day operating forecast.

## 5. Which inputs do we use, by bin?

The learner's Bin 1 fields form a **provisional candidate pool**, not a completed feature-selection or feature-engineering decision. First profile the split data, check field quality and timing, and record any transformations. Then select among these candidates for a comparable initial feature set, subject to point-in-time verification before operational use:

| Field | Learner's bin | Use |
|---|---:|---|
| `hotel` | 1 | Group bookings by property; report separately. |
| `is_repeated_guest` | 1 | Candidate predictor / lookup grouping field. |
| `previous_cancellations` | 1 | Candidate predictor / lookup grouping field. |
| `previous_bookings_not_canceled` | 1 | Candidate predictor / lookup grouping field. |

`is_canceled` is the training target and proof outcome, never a predictor. `adr`, stay nights, and cancellation outcomes are used only where required by the scoring contract for evaluation; they are not candidate model predictors. Other Bin 2 or Bin 3 columns are excluded from the candidate predictors unless a timestamped source later proves when the value becomes available and the team records a new decision. The learner's bins are recorded decisions, not independent proof of PMS timing. **Initial training-period EDA across all 32 source columns, a retain-raw decision, and provisional feature matrices are recorded in `notebooks/02_natural_language_data_prep.ipynb`.** Final feature approval and point-in-time verification are still pending.

## 6. Where do the numbers come from, and how is the buffer set and frozen?

Use `src/contract.py` without modification. Preliminary brief-number checks and the arrival-date periods existed first. The initial run in `notebooks/02_natural_language_data_prep.ipynb` has now completed the split, training-period quality/target profile, a no-cleaning decision, and provisional feature matrices. Continue and verify the full modeling workflow in this order:

1. **Initial check done:** the raw file was loaded unchanged; training shape, missing values, exact repeated rows, ranges, and candidate field distributions were inspected. Broader quality review may add checks, but do not use proof outcomes to make data-preparation decisions.
2. Create train, choose, and proof partitions with the contract by arrival date: train before 2016-07-01, choose 2016-07-01 through 2016-12-31, and proof 2017-01-01 through 2017-08-31. Confirm counts and date ranges.
3. **Initial train EDA done:** all 32 source fields were profiled for type, missingness, cardinality, common values, and numeric ranges; target balance by hotel and month and candidate-field profiles were inspected on train. Choose and proof target rates were not calculated in this notebook; proof outcomes remain reserved until settings are frozen.
4. **Initial decision recorded:** change zero raw rows/values. Keep 16,291 exact repeated training rows because no reservation ID confirms they are erroneous; leave missing non-candidate fields as-is; do not clip unusual non-negative values. Record any later change and its affected rows/values.
5. **Provisional feature preparation done:** the learner's Bin 1 fields formed the candidate pool; hotel categories came from train, and `log1p` prior-booking counts were added. No imputation was needed for these candidate inputs. Confirm timing and final features; fit any future learned preprocessing on train only and apply consistently to choose and proof.
6. **Pending:** compare the flat rule, lookup, logistic regression, shallow tree, Random Forest, XGBoost, and CatBoost with identical eligible inputs and periods. Select the method and buffer on choose under the walk ceiling, freeze all settings, and evaluate proof once.

For booking-probability methods, sum probabilities for each hotel-night to estimate cancellations. For the lookup, sum assigned historical group rates. Convert the estimate and candidate buffer into a non-negative whole-number oversell recommendation. Record the exact rounding rule in `src/backtest.py` and apply it consistently to candidates and the flat baseline.

The flat-rule hotel's cancellation rate comes from train data. Its safety margin is not specified in the client brief, so label the chosen benchmark margin as a choose-period setting, not as the client's verified production value. Compare all rules on the same nights. A rule is acceptable only if its proof-period walk rate is at most 10 per 1,000 arrivals; show cost, empty rooms, and walks together.

## 7. What is the error bill on the proof period?

**Pending Step 5.** Proof outcomes have not been evaluated for a frozen candidate, so no costs, walk counts, savings, or monthly savings are claimed here. Populate this table from the reproducible backtest after selecting the method and buffer on choose data.

| Rule | Empty rooms | Walked guests | Walks per 1,000 | Cost (EUR) | Monthly saving vs flat rule (EUR) |
|---|---:|---:|---:|---:|---:|
| Client flat-rule benchmark | Pending | Pending | Pending | Pending | 0 |
| Chosen candidate | Pending | Pending | Pending | Pending | Pending |

Report proof-period totals and hotel-level diagnostics. If monthly savings are shown, state how the proof-period result was converted to a monthly figure; do not imply it is a measured monthly run.

## 8. What does the system look like?

**Black box:** historical bookings file and fixed evaluation contract → data preparation and candidate rule/model → one row per hotel-night with recommended `k` → revenue-manager review. The proof report compares the frozen candidate with the flat rule.

**White box:** `src/data.py` obtains the supplied dataset → `src/features.py` selects and documents approved predictors → `src/backtest.py` fits/compares candidates, chooses buffers on choose data, and scores the frozen choice on proof using `src/contract.py` → `src/nightly.py` writes the requested 14-night replay table from the frozen method.

**Diagram:** `docs/architecture.png` is pending the build/MVP stage; the text above records the intended flow, not an implemented architecture.

**Production would add:** timestamped reservation snapshots and a point-in-time feature audit; connection to the hotel's source system; access control and run monitoring; an explicit revenue-manager approval/override path; drift monitoring and a retraining policy; and a pilot with per-hotel operating constraints confirmed by the client.

## 9. What are the limits?

- The source contains 119,390 bookings, two anonymized hotel categories, and dates from 2015-07-01 to 2017-08-31; it does not establish current operating conditions.
- The proof period is historical and the required 14-night command is a replay, not a live morning forecast.
- The checked train-plus-choose cancellation rate is 36.2%, while the brief's “about one in four” is a separate rough client observation. Their populations and definitions need reconciliation.
- The current flat-rule safety margin, any per-hotel walk ceiling, final approver, walk-cost ownership, override process, and operational treatment of no-shows are unconfirmed.
- Historical feature values do not, by themselves, prove availability at the original booking or intended morning decision time.
- No method, buffer, savings, proof walk rate, or vendor-accuracy claim has been validated yet.
- The supplied walk ceiling is group-wide; hotel-level reports are diagnostics unless the client specifies separate constraints.

## 10. What could go wrong?

| Risk | Effect | Response |
|---|---|---|
| Late or post-outcome information leaks into predictors | Inflated offline results that cannot be reproduced at decision time | Restrict candidates to the learner's provisional Bin 1 fields; verify snapshots before production; keep outcomes target-only. |
| Cancellation patterns change by season, hotel, or booking mix | Choose-period performance may not persist | Compare against the flat baseline, show hotel-level results, disclose the short historical span, and monitor a future pilot. |
| Sparse lookup groups or uncalibrated model probabilities | Unstable expected cancellations and poor oversell counts | Define a fallback for sparse groups, assess calibration, and select only on choose data under the walk ceiling. |
| Walks cluster at one property despite a group-wide pass | A group total can conceal a local operating problem | Report each hotel separately and ask the client whether per-hotel limits are needed. |
| Full final-book data is mistaken for morning-available data | Staff may rely on a forecast that uses future reservations | Label the result as historical replay; require timestamped snapshots for a live version. |
| Client treats the vendor's “95% accuracy” as comparable | Misleading comparison with an undefined metric | Request the metric, dates, population, and baseline; judge this project with the supplied euro and walk contract. |
| Proof is used repeatedly to tune settings | Held-out estimate becomes biased | Freeze choices first, run proof once, and disclose any post-proof change with both results. |

## 11. What is out of scope?

Automated reservation changes, hotel-system integration, live morning snapshots, unverified use of amendable or post-outcome fields, a client-approved production margin, guest segmentation without an action and value case, and a deployment claim are outside this MVP. The MVP is a reproducible historical comparison and a human-review 14-night replay. No result is presented as production-ready until the timing, approval, and operating questions above are resolved.
