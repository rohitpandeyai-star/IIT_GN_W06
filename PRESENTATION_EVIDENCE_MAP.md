# Presentation evidence map — `Hotel_Overbooking_New_Deck.pptx` (18 slides)

**Basis.**
- The model story (slides 1 and 6–18) comes from `notebooks/10–16`, with outputs in `data/models/` and `models/`.
- Slides 3–5 (data, columns, cleaning) come from the raw data and notebooks 03–07.
- Every figure passes through `presentation/deck_data.py`, which writes `presentation/deck_data.json`.
  - `presentation/build_deck.py` builds slides 1–5.
  - It then runs `presentation/deck_nb11_16.py` for slides 6–12 and 18, which runs `presentation/deck_leads.py` for slides 13–17.
  - Neither reads any figure from anywhere other than that JSON file.

**Rebuild:** `python presentation/deck_data.py && python presentation/build_deck.py`

**Periods** (fixed by `src/contract.py`, which is unchanged):

| Period | Arrivals | Bookings | Used for |
|---|---|---|---|
| Train | before Jul 2016 | 49,157 | fitting models |
| Validation (contract "choose") | Jul–Dec 2016 | 29,546 | choosing the model and buffers |
| 2017 test (contract "proof") | Jan–Aug 2017 | 40,687 | testing |

**The test period was scored twice:**
- **Run 1:** frozen before any test result.
- **Run 3:** decided after run 1's result was seen.

The deck reports both runs and says which came first.

**Cost:** `contract.night_cost` = empty rooms × the night's mean booked stay value + walked guests × €300.
**Walk limit:** 10 walked guests per 1,000 arrivals, group-wide.

| Slide | Figure | Value | Source | Period |
|---|---|---|---|---|
| 1 | Flat rule's test cost and walks | €3,214,912; 7.18 per 1,000 | `data/models/test_results_primary.csv` | Test (run 1) |
| 1 | CatBoost's extra cost | +€150,459 | same | Test (run 1) |
| 1 | Walks after refitting | 13.1 per 1,000 (CatBoost 13.11, XGBoost 13.07) | `data/models/test_run3_results_primary.csv` | Test (run 3) |
| 2 | Cost rule, €300, limit 10, periods | as stated | `BRIEF.md`, `docs/EVALUATION_CONTRACT.md`, `src/contract.py` | — |
| 3 | Bookings; City / Resort cancellation rates; monthly chart | 119,390; 41.73% / 27.76%; 26 months × 2 hotels | `data/hotels.csv` → `deck_data.json` `data` | All |
| 4 | Column decisions: inputs / provisional / excluded | 4 / 4 / 36 of 44 | `notebooks/06_forecast_column_selection.ipynb` decision cells → `deck_data.json` `columns` | — |
| 4 | Reasons | as stated | `notebooks/06_…`, `07_forecast_columns_explained.ipynb` | — |
| 5 | C1 meal "Undefined" → "SC" | 1,169 rows | raw recount in `deck_data.py`, asserted equal to the notebook 05 log | All |
| 5 | C2 agent / company blanks → "none" | 16,340 / 112,593 | same | All |
| 5 | C3 country blanks → "unknown"; C4 children blanks → 0 | 488; 4 | same | All |
| 5 | C5 rows kept; C6 previous_cancellations unchanged | 0 removed | `notebooks/03_duplicate_investigation.ipynb`, `05_apply_cleaning_decisions.ipynb`, `docs/DECISIONS.md` | — |
| 6 | Encoded columns; leakage checks; infrequent threshold | 143; 16 passed; under 30 Train bookings | `notebooks/10_preprocessing_leakage_checked.ipynb`, `data/preprocessed/feature_names.json` | Train |
| 6 | Model settings (LR C = 1; RF 300 trees, leaf 20; XGBoost and CatBoost 300 rounds, depth 4, rate 0.05; seed 0) | as stated | `notebooks/11_train_models.ipynb` | — |
| 7 | In-sample log loss / Brier / AUC / nightly error | flat 0.638 / 0.224 / 0.582 / 9.67; LR 0.462 / 0.152 / 0.817 / 6.16; RF 0.480 / 0.157 / 0.810 / 6.47; XGBoost 0.458 / 0.152 / 0.815 / 6.40; CatBoost 0.459 / 0.152 / 0.815 / 6.39 | `data/models/train_scores.csv`, `train_nightly_scores.csv` | Train |
| 7 | Flat-rule hotel rates | City 41.7%, Resort 25.2% | `models/frozen_choice.json` | Train |
| 8 | Validation AUC / log loss | flat 0.557 / 0.652; LR 0.705 / 0.611; RF 0.701 / 0.601; XGBoost 0.714 / 0.606; CatBoost 0.702 / 0.606 | `data/models/val_scores.csv` | Validation |
| 8 | Predicted rate (actual 36.9%) and City nightly bias | flat 36.4%, +1.0; LR 28.1%, −11.1; RF 29.3%, −9.8; XGBoost 27.8%, −11.5; CatBoost 27.9%, −11.3 rooms | `data/models/val_nightly_scores.csv` | Validation |
| 8 | Bookings with a prior cancellation | 11.8% (Train) → 1.3% (validation) | `deck_data.json` `data.prior_cancellation_share`; `notebooks/13_…` | Train / Validation |
| 9 | One shared buffer: rooms, cost | flat 16, €2.41M; LR 6, €2.16M; RF 6, €2.04M; XGBoost 5, €2.03M; CatBoost 5, €2.03M | `data/models/val_results.csv` | Validation |
| 9 | Per-hotel buffer: City / Resort, cost | flat 20/4, €1,950,066; LR 5/6, €2.11M; RF 7/5, €2.01M; XGBoost 6/3, €1.93M; CatBoost 6/3, €1,922,977 | recomputed in `deck_data.py` from `data/models/val_probabilities.csv`; asserted equal to notebook 13 | Validation |
| 9 | Resamples / months in which CatBoost (per-hotel) beat the flat rule | 74% / 3 of 6 | `notebooks/13_validation_results_explained.ipynb` | Validation |
| 10 | CatBoost cheaper than XGBoost in resamples | 91% | same | Validation |
| 10 | Freeze | CatBoost City 6 / Resort 3; benchmark flat rule 20 / 4; frozen 2026-11-18 01:57:07 | `models/frozen_choice.json`, `docs/DECISIONS.md` | — |
| 11 | Group: cost, empty rooms, walked, per 1,000 | flat €3,214,912 / 7,166 / 179 / 7.18; CatBoost €3,365,371 / 7,322 / 210 / 8.42 | `data/models/test_results_primary.csv` | Test (run 1) |
| 11 | By hotel: cost, per 1,000 (flat / CatBoost) | City €1.95M / €1.93M, 4.80 / 7.33; Resort €1.27M / €1.44M, 11.29 / 10.30 | same | Test (run 1) |
| 11 | Months CatBoost cheaper; accuracy; "nobody cancels"; AUC | 3 of 8; 63.5%; 61.3%; 0.679 | `notebooks/14_test_run.ipynb`, `data/models/test_accuracy.csv` | Test (run 1) |
| 12 | Run 3 cost and walks | CatBoost €2,804,174, 13.11; XGBoost €2,799,388, 13.07; flat rule with Train + validation rates €3,193,614, 8.10 | `data/models/test_run3_results_primary.csv`, `models/frozen_choice_run3_train_val.json` (frozen 02:05:41) | Test (run 3) |
| 12 | Refit columns; extra expected cancellations per City night | 167; +5.0 (CatBoost 4.96) | `notebooks/15_retrain_train_val.ipynb` | Train + validation |
| 12 | Run 2 | XGBoost on Train, frozen, never run | `models/frozen_choice_run2_xgboost.json`, `docs/DECISIONS.md` | — |
| 13 | Client Lead: median stay value; cheapest buffer without the limit and its walks | City €328, Resort €380; 0 rooms for every method, 22–82 walks per 1,000 | `data/models/val_buffer_sweep.csv`, `contract.nightly_table` on validation → `deck_data.json` `nb.leads` | Validation |
| 14 | Data Lead: prior-cancellation share; Train rate without repeats; checks | 11.8% → 1.3%; 35.8% → 22.2%; 16 checks, 30-booking pooling | as for slides 5, 6 and 8 | Train / Validation |
| 15 | Model Lead: example night; validation AUC; Train mean prediction | Σ p = 24.56 vs 30 cancelled; XGBoost 0.714; 35.8% | `data/models/val_probabilities.csv`, `val_scores.csv`, `train_scores.csv` | Train / Validation |
| 16 | Model Lead: newsvendor ratio V / (V + €300); CatBoost buffer 0 → 5 | 0.52–0.56; €1.43M → €2.03M, 22.9 → 8.5 walks per 1,000; flat 0 → 16 | `deck_data.json` `nb.leads` (from `val_buffer_sweep.csv`) | Validation |
| 17 | Build Lead: nightly command, fingerprints, inputs, contract tests | `python src/nightly.py --from 2017-08-18 --nights 14` runs the frozen choice; expected counts equal notebook 14's predictions | `src/nightly.py`, `tests/test_nightly.py`, `models/frozen_choice.json`, `src/features.py`, `tests/` | Test period, inference only |
| 18 | Conclusion | restates slides 11–12; next steps are proposals only | `docs/ROADMAP.md` is blank | — |

The newsvendor ratio on slide 16 is theory used to explain the sweep. It was not a rule the notebooks fitted.

**Hotel-level results** are reported separately. The contract gives no per-hotel walk threshold, so the Resort's 11.29 and 10.30 are not called breaches.

**Separate pipeline re-check.** `notebooks/pipeline/05–14` (outputs in `evidence/`) is a later, separate re-run.
- It is mentioned only in slide 12's notes.
- It also kept the flat rule (`docs/PIPELINE_VALIDATION.md`).
- Its figures are not in this deck.
