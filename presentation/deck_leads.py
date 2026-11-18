# Lead-decision slides: the theory and logic behind each role's decisions (all four roles: Rohit Pandey, docs/CHARTER.md).
# Executed by deck_nb11_16.py before the conclusion. Uses the helpers and data already defined there.
LD = NB["leads"]
UN = LD["unconstrained"]
OWNER = "Rohit Pandey"


def lead_table(s, rows, y=2.3, row_h=0.74):
    head = [["Decision", "Theory behind it", "How it played out here"]]
    hl = {(r, 0): ((TINT if r % 2 == 0 else PAPER), INK, True) for r in range(1, len(rows) + 1)}
    table(s, 0.6, y, 12.15, head + rows, [2.75, 4.5, 4.9], row_h=row_h, size=11, highlight=hl, align=[L, L, L])


walk_range = f"{min(u['walks_per_1000'] for u in UN.values()):.0f}–{max(u['walks_per_1000'] for u in UN.values()):.0f}"

# ============================================================ Client Lead
s = frame(f"12 · Client Lead · {OWNER}", "What is decided, for whom, and at what cost per wrong call?",
          "Price both errors in euros, make walks a hard limit, and judge every model against the client's own rule on equal terms",
          "BRIEF.md · docs/EVALUATION_CONTRACT.md · src/contract.py · data/models/val_buffer_sweep.csv · docs/DECISIONS.md",
          "The Client Lead frames the decision so that every method is judged by what the revenue manager actually does. One whole number per hotel-night, "
          "because that is the decision; booking accuracy says little (63.5% against 61.3% for predicting nobody cancels). Both errors are priced in euros: an "
          f"empty room loses that night's average stay value (median {eur(LD['median_stay_value']['City Hotel'])} at the City Hotel, "
          f"{eur(LD['median_stay_value']['Resort Hotel'])} at the Resort on validation) and a walk costs €300. Walks are a hard limit, not a price, because "
          f"without the limit every method's cheapest buffer on validation is 0 rooms, walking {walk_range} guests per 1,000. The benchmark is the client's "
          "flat rule given the same buffer freedom, so only the forecast differs: with one shared buffer the models looked 16% cheaper, with per-hotel buffers "
          "for all only 1.4%. The limit is group-wide because that is what the contract states; hotel figures are reported, not judged.")
lead_table(s, [
    ["One whole number per hotel-night", "Score a decision in the unit it is taken: the revenue manager sets rooms per night, not a label per booking",
     "Booking probabilities are summed per night (contract.nightly_table); accuracy 63.5% vs 61.3% for 'nobody cancels' shows booking scores say little"],
    ["Price both errors in euros", "Asymmetric loss: an empty room loses the night's stay value, a walked guest costs €300; one scale ranks all methods",
     f"Median stay value on validation: City {eur(LD['median_stay_value']['City Hotel'])}, Resort {eur(LD['median_stay_value']['Resort Hotel'])} — an empty room usually costs more than a walk"],
    ["Walks are a hard limit, not a price", "Constrained optimisation: a brand harm the client will not trade for money is a constraint, not a cost term",
     f"Without the limit every method's cheapest buffer is 0 rooms, walking {walk_range} per 1,000; run 3 was cheaper but rejected at 13.1"],
    ["Benchmark: the flat rule, same freedom", "A fair counterfactual changes one thing at a time: only the forecast may differ between the rule and a model",
     "One shared buffer: models 16% cheaper. A buffer per hotel for every method: CatBoost only 1.4% cheaper"],
    ["Group-wide limit; hotels reported", "Do not invent requirements the client has not stated (project rule 6)",
     "Resort walked 11.29 per 1,000 under the flat rule on the test: reported, not called a breach; a per-hotel limit is an open client question"]])

# ============================================================ Data Lead
s = frame(f"13 · Data Lead · {OWNER}", "What did the hotel know on the decision morning?",
          "Columns were admitted by timing, not by score, and nothing from later periods or the outcome shaped the data",
          "notebooks/03–07, 10 · src/features.py · tests/test_features.py · docs/DECISIONS.md · src/contract.py (periods)",
          "The Data Lead's theory is target leakage: a field written after the outcome predicts well on every period, so no score can expose it; only timing "
          "can. So 8 of 44 columns were admitted by four timing tests, and src/features.py plus tests/test_features.py keep the list fixed. Four columns were "
          "unsure on timing and used provisionally, with the risk named; it came true, as the share of bookings with a prior cancellation fell from 11.8% in "
          "Train to 1.3% in validation. The 31,994 exact repeats were kept, because removing rows changes both the label (Train rate 35.8% to 22.2%) and the "
          "nights the contract scores, and no booking ID proves they are errors. The split is by arrival date, because the model must forecast forward. Every "
          "statistic in the encoding is fitted on Train only and no step uses the label: 16 leakage checks pass.")
lead_table(s, [
    ["Admit columns by timing tests", "Target leakage: a field written after the outcome predicts well on every period, so no score can expose it",
     "8 of 44 admitted; reservation status, assigned room and deposit type excluded; tests/test_features.py fails if a held-back column returns"],
    ["Use 4 'unsure' columns, flagged", "A stated assumption is a testable risk; a hidden one is not",
     f"The risk came true: bookings with a prior cancellation fell from {DATA['prior_cancellation_share']['Train']:.1%} (Train) to {DATA['prior_cancellation_share']['Choose']:.1%} (validation)"],
    ["Keep the 31,994 exact repeats", "Removing rows changes the label distribution and the population scored (selection bias)",
     f"Train rate would fall {CL['train_rate_all_rows']:.1%} → {CL['train_rate_without_repeats']:.1%}; no booking ID proves an error; flags added instead"],
    ["Split by arrival date", "Temporal validation: forecast forward, as in use; a random split leaks future rows and repeats across sets",
     "Contract periods: Train before Jul 2016, validation Jul–Dec 2016, test Jan–Aug 2017"],
    ["Fit on Train only; no target encoding", "Any statistic from later rows or from the label is information the model would not have",
     f"{NB['nb10']['checks']} leakage checks pass; categories under {NB['nb10']['min_bookings']} Train bookings pooled; a shuffled label gives identical output"]])

# ============================================================ Model Lead 1: probabilities
s = frame(f"14 · Model Lead · {OWNER}", "How many will cancel tonight, and how sure are we?",
          "Each booking gets a probability and their sum is the night's expected cancellations, so the level matters as much as the ranking",
          "notebooks/11_train_models.ipynb, 12_validate_models.ipynb, 13_validation_results_explained.ipynb · src/contract.py (nightly_table)",
          "The Model Lead's core theory is linearity of expectation: whatever the dependence between bookings, the expected number of cancellations on a night "
          "is the sum of the bookings' probabilities. contract.nightly_table does exactly that, and also gives a spread, the square root of the sum of p(1-p), "
          "if bookings cancel independently. Because the probabilities are added, they must be right in level: proper scoring rules (Brier, log loss) reward "
          "that; ROC AUC only rewards ranking, which is why XGBoost's best AUC did not decide. No class rebalancing, because it shifts every probability. Four "
          "families cover the bias-variance range: a linear model, a bagged forest and two boosted ensembles. Settings were fixed in advance, because every "
          "choice made on validation inflates validation; the validation edge was already small and unreliable.")
rect(s, 0.6, 2.2, 12.15, 0.72, TINT, radius=0.08)
text(s, 0.85, 2.27, 11.7, 0.6, [[("Expected cancellations = Σ pᵢ", {"bold": True, "font": HEAD, "size": 17}),
                                 ("     spread = √ Σ pᵢ(1 − pᵢ) if independent", {"size": 14, "color": MUTED}),
                                 ("     City, 4 Jul 2016: Σ p over 92 bookings = 24.56; 30 cancelled", {"size": 14, "color": MUTED})]],
     anchor=MSO_ANCHOR.MIDDLE)
lead_table(s, [
    ["Predict per booking, then add up", "Linearity of expectation: the expected count is the sum of the probabilities, whatever the dependence",
     "Uses each booking's details; a nightly-count model would have only 732 Train rows"],
    ["Proper scoring rules over AUC", "Brier and log loss are minimised only by the true probability; AUC rewards order and ignores level",
     f"XGBoost had the best validation AUC ({VA[XG]['auc']:.3f}), yet every model predicted about 28% against {VA[CB]['actual']:.1%}"],
    ["No class weights or resampling", "Rebalancing pushes every probability away from the real rate, so the nightly sum would be biased",
     f"On Train every model's mean prediction matches the actual rate, {CL['train_rate_all_rows']:.1%}"],
    ["Four families plus the flat rule", "Bias–variance: linear (stable, rigid), bagging (cuts variance), boosting (cuts bias step by step)",
     f"All fit Train alike (AUC {TR[RF_]['auc']:.2f}–{TR[LR_]['auc']:.2f}) and all fell to about 0.70: the limit was the data shift, not the family"],
    ["Fixed settings, no tuning", "Every choice made on validation inflates validation results (selection bias, the winner's curse)",
     f"Settings written before any result; the validation edge was already small (−1.4%) and unreliable ({NB['resample_cheaper_than_flat'][CB]:.0%} of resamples)"]],
    y=3.1, row_h=0.6)

# ============================================================ Model Lead 2: the oversell and its buffer
cb_u, fl_u = UN["CatBoost"], UN["flat-rule reference"]
cr = LD["critical_ratio"]
s = frame(f"15 · Model Lead · {OWNER}", "How many rooms to oversell, and how was that chosen?",
          "Economics says oversell the expected count; the walk limit forces a buffer, so the cheapest one inside it was taken",
          "notebooks/12_validate_models.ipynb (buffer sweep), 13_validation_results_explained.ipynb · data/models/val_buffer_sweep.csv · models/frozen_choice.json",
          "Theory first. With an empty room costing the stay value V and a walk costing €300, the cost-minimising oversell, ignoring the limit, is the point where "
          "the chance that cancellations fall short of it equals V / (V + 300) — the newsvendor critical ratio. With median V of about €330–380 that is "
          f"{cr['City Hotel']:.2f}–{cr['Resort Hotel']:.2f}: oversell about as many rooms as you expect to cancel, no safety margin. The validation sweep agrees: "
          f"every method's cheapest buffer is 0 rooms, but that walks {walk_range} guests per 1,000. So the walk limit binds, and the buffer is the price of "
          f"keeping it: CatBoost's shared buffer 0 → 5 raised its cost from {m(cb_u['cost'])} to {m(cb_u['chosen_cost'])} and cut walks from "
          f"{cb_u['walks_per_1000']:.1f} to 8.5. The rule floor(expected) − buffer is one auditable integer per hotel; every method gets per-hotel buffers; "
          "uncertainty is measured by resampling weeks, because neighbouring nights are alike; and the choice was frozen with fingerprints before the test.")
rect(s, 0.6, 2.2, 5.9, 1.3, INK, radius=0.05)
text(s, 0.85, 2.3, 5.4, 0.3, "THEORY · THE NEWSVENDOR RATIO", size=11, color=ORANGE, bold=True)
text(s, 0.85, 2.62, 5.4, 0.85, [[("Cheapest oversell, ignoring the limit: ", {"color": "C9D2DA"}),
                                 (f"the {cr['City Hotel']:.2f}–{cr['Resort Hotel']:.2f} quantile of cancellations", {"bold": True, "color": PAPER})],
                                [(f"V / (V + €300), median stay value V ≈ {eur(LD['median_stay_value']['City Hotel'])}–{eur(LD['median_stay_value']['Resort Hotel'])}: no margin", {"color": "C9D2DA"})]], size=13)
rect(s, 6.85, 2.2, 5.9, 1.3, TINT, radius=0.05)
text(s, 7.1, 2.3, 5.4, 0.3, "EVIDENCE · VALIDATION SWEEP", size=11, color=ORANGE, bold=True)
text(s, 7.1, 2.62, 5.4, 0.85, [[("Without the limit, every method's cheapest shared buffer is 0", {"bold": True})],
                               [(f"…walking {walk_range} per 1,000. With the limit: CatBoost 0 → 5 rooms, "
                                 f"{m(cb_u['cost'])} → {m(cb_u['chosen_cost'])}; flat rule 0 → {fl_u['chosen_buffer']}", {"color": MUTED})]], size=13)
lead_table(s, [
    ["Oversell = ⌊expected⌋ − buffer", "One integer per hotel: simple to audit and to explain; rounding down is the cautious direction",
     "The same rule for every method, including the flat rule"],
    ["Buffer: cheapest inside the limit", "Constrained optimisation; the limit binds, so the buffer is the price of keeping it",
     "Every City / Resort pair from 0 to 60 tried (61 × 61); CatBoost 6 / 3, flat rule 20 / 4"],
    ["Resample weeks, not nights", "Block bootstrap: neighbouring nights share season and events; resampling nights overstates certainty",
     f"27 weeks × 4,000 draws: CatBoost cheaper than the flat rule in {NB['resample_cheaper_than_flat'][CB]:.0%} — not reliable"],
    ["Freeze before the test", "Pre-registration: a choice fixed before the result cannot be bent by it",
     "models/frozen_choice.json with file fingerprints; run 3, decided after run 1, is disclosed and breached the limit"]],
    y=3.7, row_h=0.62)

# ============================================================ Build Lead
s = frame(f"16 · Build Lead · {OWNER}", "What could the revenue manager use tomorrow morning?",
          "One command replays the frozen choice for any nights — not a live tool yet: the data has no morning snapshots",
          "src/nightly.py · tests/test_nightly.py · models/frozen_choice.json · notebooks/14_test_run.ipynb · src/features.py · src/contract.py · presentation/deck_data.py",
          "The Build Lead's job is that every number can be rerun and nothing moves silently. One command, python src/nightly.py --from 2017-08-18 --nights 14, "
          "loads the frozen choice, checks the SHA-256 fingerprints of the model and preprocessor recorded at the freeze, refuses to run if either changed, and "
          "prints for each hotel and night the bookings on the books, the expected cancellations and the oversell: the recommended flat rule first (City 20, "
          "Resort 4), the frozen CatBoost alongside (6 and 3). It never fits anything and never reads the outcome column; tests/test_nightly.py checks that its "
          "expected counts equal notebook 14's saved predictions. The inputs are defined once in src/features.py; the scoring rule src/contract.py is unchanged "
          "and tested; every deck number is read from notebook outputs by presentation/deck_data.py. What is not claimed: a live morning forecast. The input is the "
          "final-book export, so this is a historical replay; a real morning run needs timestamped reservation snapshots.")
lead_table(s, [
    ["One command, frozen choice", "Inference only: the nightly tool loads what was frozen and never refits, so it cannot drift from what was tested",
     "python src/nightly.py --from 2017-08-18 --nights 14: flat rule first, CatBoost alongside; tests/test_nightly.py checks it equals notebook 14"],
    ["Fingerprints checked before predicting", "Reproducibility: same files and inputs give the same number; any change must be visible",
     "SHA-256 of the model and preprocessor must match models/frozen_choice.json, or the command refuses to run"],
    ["One definition of the inputs", "A single source prevents training/serving skew",
     "src/features.py lists the 8 inputs; the command checks the frozen preprocessor uses exactly those"],
    ["Fixed yardstick, traced numbers", "The scoring rule must not move with the method, and a number without a source cannot be defended",
     "src/contract.py untouched and tested; presentation/deck_data.py reads notebook outputs and asserts key figures"],
    ["No live morning claim", "Point-in-time correctness: a forecast may use only what existed at decision time (project rule 7)",
     "The input is the final-book export: the command is a historical replay and never reads outcomes; snapshots are needed"]])
