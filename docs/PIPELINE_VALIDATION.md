# Pipeline 05–14: execution and validation report

**Run:** 2026-11-18, `notebooks/pipeline/05`–`14`, executed in order on Python 3.14.5, pandas 3.0.6, numpy 2.5.3, scikit-learn 1.9.1, XGBoost 3.4.1. Data `data/hotels.csv`, SHA-256 `d10cdeb0…`, 119,390 rows. Full record: `evidence/pipeline_run/run_manifest.json`; file provenance: `evidence/pipeline_run/provenance.json`.

> **Historical disclosure.** The Proof period was inspected in earlier project work (`docs/DECISIONS.md`, 2026-11-18). Notebook 12's Proof figures are a **retrospective** evaluation of a configuration frozen before notebook 12 ran. They are not a historically blind test.

> **What this is not.** A historical simulation under the client's contract. Booking rows stand in for rooms; "walks" are simulated, not observed relocations; no room inventory exists; feature timing is not verified at booking time; the nightly pipeline has no as-of booking snapshot. None of this is production-ready.

## 1. Architecture and execution order

| Stage | Notebook | Reads | Writes |
|---|---|---|---|
| Feature table | `05_feature_engineering` | `src/data.py` | `evidence/feature_engineering/` |
| Probability baselines | `06_baselines_and_pooling_lab` | `src/data.py`, `src/contract.py` | `evidence/baselines_pooling/` |
| Model experiments | `07_train_model_experiments` | same | `evidence/train_model_experiments/` |
| Hyperparameters (expanding folds in Train) | `08_hyperparameter_experiments` | same | `evidence/hyperparameter_experiments/selected_settings.csv` |
| Calibration | `09_probability_calibration` | 08's selection | `evidence/probability_calibration/calibration_decision.json` |
| Uncertainty and conformal | `10_uncertainty_and_conformal` | 08's selection | `evidence/uncertainty_conformal/` |
| Policy selection on Choose | `11_choose_policy_selection` | 08, 09 | `evidence/choose_policy_selection/frozen_configuration.json` |
| Frozen Proof evaluation | `12_proof_evaluation` | the frozen configuration only | `evidence/proof_evaluation/` |
| Benchmark evidence review | `13_ai_benchmark` | `evidence/expanded_benchmark/` | `evidence/ai_benchmark_review/` |
| Nightly pipeline audit | `14_nightly_pipeline_validation` | `src/nightly.py`, `src/features.py`, `models/xgboost*` | `evidence/nightly_pipeline_validation/` |

Every notebook rebuilds the data from `data.read_raw()` and splits it with `contract.split_periods`; `src/contract.py` is unchanged. **All ten notebooks executed with no error cells**; `pytest -q`: **11 passed**.

## 2. What had to be fixed, and why

| Problem found | Fix | Where |
|---|---|---|
| Notebooks, `src/features.py`, `src/nightly.py`, `tests/test_nightly.py`, `models/xgboost*`, the benchmark evidence and nightly outputs existed only outside the repository | Copied in unchanged; hashes recorded | `evidence/pipeline_run/provenance.json` |
| Notebooks import `src` and write relative paths, so they fail when opened from their own folder | First cell moves to the repository root | every notebook |
| 09–12 hard-coded `logistic_regression, C=1.0` (and 12 `model_buffer_1.0`) as placeholders to be copied by hand; 08 actually selected **C = 0.1** | They now read 08's `selected_settings.csv`; 12 reads only the frozen configuration and checks the 08/09 evidence hashes | 09–12 |
| 09 left the calibration decision undecided | Rule fixed before running (both Choose Brier and log loss must improve); decision and the fitted mapping saved | 09 |
| 11 had no contract flat rule with a margin (rule 5), and every model buffer only **added** rooms | Declared families added: `flat_rule_margin_m` and `model_margin_m`, m = 0…60; all declared policies kept | 11 §8b |
| `country` held back in the notebooks but used by `src/features.py` and the nightly schema | `features.py` matches notebook 05; `tests/test_features.py` guards it; `nightly.py` validates against `features.py` | `src/`, `tests/` |
| 14's checklist statuses were typed in as "Pending" | Statuses now computed from the run and saved | 14 |

## 3. Baselines versus machine learning (Choose, 368 hotel-nights)

| Method | Brier | Log loss | ROC AUC | Nightly count MAE (rooms) |
|---|---|---|---|---|
| Global rate | 0.2329 | 0.6585 | 0.500 | 9.66 |
| Hotel rate / pooled (m = 20, 50, 100) | 0.2299 | 0.6520 | — | 9.19 |
| Logistic regression (07 default) | 0.2110 | 0.6171 | 0.699 | 9.91 |
| Random forest (07 default) | 0.2103 | 0.6073 | 0.691 | **8.88** |
| Selected: logistic regression C = 0.1 (08) | 0.2091 | 0.6105 | — | — |
| Selected, calibrated (09) | **0.2011** | **0.5857** | — | — |

Partial pooling changes nothing in practice (each hotel has tens of thousands of bookings). The models improve booking-level probabilities over the baselines, but only the random forest improves the nightly count error. Sources: `evidence/baselines_pooling/`, `evidence/train_model_experiments/`, `evidence/hyperparameter_experiments/`.

## 4. Selected model and hyperparameters

**Logistic regression, C = 0.1** (lowest mean chronological validation Brier, 0.1731 over three expanding folds; the random forest with 100 trees and leaf 10 had better log loss, 0.530 against 0.546, but Brier was the declared criterion). `evidence/hyperparameter_experiments/candidate_summary.csv`.

## 5. Calibration

Sigmoid (Platt) mapping fitted on out-of-fold Train predictions only (first date block excluded): `calibrated = 1/(1+exp(−(−2.332 + 5.954·p)))`. On Choose: Brier 0.2091 → **0.2011**, log loss 0.6105 → **0.5857**, mean probability 0.285 → 0.360 (actual 0.369). **Adopted** under the pre-declared rule. It improved the City Hotel (Brier 0.2172 → 0.2053) and slightly worsened the Resort (0.1915 → 0.1919). `evidence/probability_calibration/`.

## 6. Uncertainty and conformal intervals (Choose)

| Interval (nominal 90%) | Coverage, group | City | Resort | Mean width (rooms) |
|---|---|---|---|---|
| Normal approximation | **41.6%** | 37.0% | 46.2% | 11.6 |
| Split conformal (quantile 36.9 rooms, 148 calibration nights) | 94.3% | 89.1% | 99.5% | **53.2** |

The independence assumption behind the normal interval fails badly: cancellations are correlated (group blocks, shared events). Split conformal reaches roughly the nominal level but is too wide to act on, and its exchangeability assumption is broken by time order and drift, so **no coverage guarantee is claimed**. These are cancellation-count intervals, not capacity intervals. `evidence/uncertainty_conformal/`.

## 7. Policy comparison and selection (Choose)

Rule: drop every policy above 10 walks per 1,000 arrivals; take the lowest cost.

| Policy | Cost (EUR) | Empty rooms | Walks | Walks per 1,000 | Ceiling |
|---|---|---|---|---|---|
| **Flat rule, margin 17 — selected** | **2,414,409** | 5,532 | 169 | 9.06 | met |
| Model (calibrated LR), margin 18 | 2,576,784 | 5,934 | 182 | 9.76 | met |
| No overbooking | 4,155,341 | 10,894 | 0 | 0.00 | met |
| Model expected / buffers 0.25–2.0 (declared) | 932,629–1,129,359 | 486–1,419 | 1,342–3,232 | 72–173 | **breached** |
| Global, hotel, hotel-month rates (margin 0) | 1,130,028–1,492,664 | 1,670–1,954 | 1,725–2,511 | 92–135 | **breached** |

**Selected: the client's own flat rule with a margin of 17 rooms.** No model-based policy beat it under the ceiling. By hotel at the selected policy: City Hotel 13.96 walks per 1,000, Resort 0.30 (diagnostic; no per-hotel threshold was given). `evidence/choose_policy_selection/`.

## 8. Proof (retrospective; frozen before notebook 12 ran)

| | Cost (EUR) | Empty rooms | Walks | Walks per 1,000 | Ceiling |
|---|---|---|---|---|---|
| **Frozen: flat rule, margin 17** | **3,935,876** | 8,186 | 155 | **6.21** | **met** |
| Declared benchmark: model margin 18 | 4,172,660 | 8,615 | 277 | 11.11 | breached |

By hotel (frozen policy): City Hotel EUR 1,640,857, 9.23 walks per 1,000; Resort Hotel EUR 2,295,019, 0.99. The model benchmark cost EUR 236,784 more and breached the ceiling. `evidence/proof_evaluation/`.

## 9. Benchmark evidence (`evidence/expanded_benchmark/`)

26 of 27 configurations completed; best CV Brier: balanced random forest (0.147). Its Choose-selected policies cost far less (about EUR 1.3 million) than anything in this pipeline, **but the benchmark is not comparable**: it used `country`, which this pipeline holds back; its source code (`src/run_cv_benchmark.py`, `src/mlops_tracking.py`) is not in the repository, so it cannot be reproduced; and its Proof rows were already exposed (7 of 22 Choose-selected policies breached the ceiling on Proof). `evidence/ai_benchmark_review/`.

**Assignment AI build:** not available — no `ai-benchmark` branch and no `ai_benchmark/PLAN_AI.md`, `run.py`, `RESULT.md`. No AI findings are recorded (`docs/COMPARISON.md`).

## 10. Nightly inference pipeline

| Check | Result |
|---|---|
| Code feature schema | Reconciled: `country` removed; guarded by `tests/test_features.py` |
| Saved model schema | **Mismatch:** `models/xgboost.joblib` was trained with `country` |
| Historical smoke test | **Fails by design:** `nightly.py` rejects the stale artifact with a schema error |
| Artifact versions | Pickled with scikit-learn 1.8.0 / XGBoost 3.1.3; 11 version warnings on load here |
| Synthetic aggregation test | Passed |
| Conformal rank test | Passed (rank 2, value 1.0 for 148 residuals, α = 0.01) |
| As-of snapshot | Not implemented |

The earlier smoke-test output in `outputs/nightly_recommendations.csv` was produced by the `country` model and proves only code execution and shape. The nightly policy (99% lower conformal bound with XGBoost) is also **not** the policy selected in notebook 11. `evidence/nightly_pipeline_validation/`.

## 11. Production blockers

1. No as-of active-booking snapshot; the final export includes bookings made after, or cancelled before, any decision time.
2. Feature timing unverified; four inputs are provisional (`docs/DECISIONS.md` P3).
3. No room inventory, rooms-per-booking or observed walk records.
4. The nightly artifact uses a held-back feature, was built with older library versions, and implements a different policy from the one selected.
5. The walk ceiling binds every policy; the City Hotel carries most of the walks, which a group-wide ceiling hides.
6. Proof has been exposed; any further change needs a new evaluation design and a period not yet seen.

## 12. Recommended next steps

1. Decide what the nightly pipeline should implement. On this evidence it is the flat rule with a margin of 17 rooms, which needs no model; if a model is kept, retrain it on the approved features with current library versions and reconcile its policy with notebook 11.
2. Add an `--as-of` input contract to `src/nightly.py`, scoring only bookings known and active at the decision time.
3. Obtain timestamped PMS snapshots to verify feature timing and rebuild the four provisional inputs as of the decision time.
4. Ask the client whether the walk ceiling also applies per hotel; on Choose the City Hotel runs above 10 per 1,000 under the selected policy.
5. Run the assignment AI benchmark on its own branch as `docs/AI_WORKFLOW.md` requires, then complete `docs/COMPARISON.md`.
6. Pin numpy to the version in `requirements.txt` (2.5.4; this run used 2.5.3) and confirm the pipeline on Python 3.12, the version the project container uses.
