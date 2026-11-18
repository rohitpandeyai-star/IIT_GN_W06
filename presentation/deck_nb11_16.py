# Slides that follow notebooks 10-16. Executed by build_deck.py after the shared slides (decision, data, columns, cleaning).
# Uses the helpers and data already defined there.
NB = D["nb"]
TR, VA = NB["train"], NB["val"]
FL, LR_, RF_, XG, CB = "flat-rule reference", "logistic regression", "random forest", "XGBoost", "CatBoost"
LABEL = {FL: "Flat rule (hotel rate)", LR_: "Logistic regression", RF_: "Random forest", XG: "XGBoost", CB: "CatBoost"}
R1 = {(r["hotel"], r["method"]): r for r in NB["run1"]["rows"]}
R3 = {(r["hotel"], r["method"]): r for r in NB["run3"]["rows"]}
FLAT1, CAT1 = R1[("group", "flat rule")], R1[("group", "CatBoost")]
CAT3, XGB3 = R3[("group", "CatBoost")], R3[("group", "XGBoost")]
FLAT3F = R3[("group", "flat rule (train + val rates)")]
EVH = {m: EV[m]["per_hotel"] for m in EV}


def pct(a, b):
    return f"{a / b - 1:+.1%}"


# ============================================================ 6. Encoding and settings (notebooks 10-11)
s = frame("5 · Encoding and settings", "How was the data encoded, and how were the models set up?",
          f"{NB['nb10']['columns']} encoded columns learnt from Train only; {NB['nb10']['checks']} leakage checks passed; every setting fixed before results were seen",
          "notebooks/10_preprocessing_leakage_checked.ipynb · notebooks/11_train_models.ipynb · data/preprocessed/feature_names.json",
          f"Notebook 10 builds the encoded table. The 5 categorical inputs are one-hot encoded; categories with fewer than {NB['nb10']['min_bookings']} Train bookings, "
          "and any value never seen in Train, share one 'infrequent' column, and the hotel becomes a single 0/1 column. The two prior-booking counts are "
          "log-transformed (log of 1 + count) and scaled with the Train mean and standard deviation; the repeat-guest flag is kept as 0/1. "
          f"That gives {NB['nb10']['columns']} columns. Everything is fitted on Train only, and {NB['nb10']['checks']} leakage checks passed twice: no outcome "
          "column, statistics equal to Train's, a shuffled label gives identical output, rows transformed independently, nothing but the 8 inputs in the output, "
          "test never opened. Notebook 11 then fixes modest settings for four models before seeing any result, with seed 0 and no class rebalancing, because "
          "the contract adds the probabilities up and they must stay on the real scale.")
cards = [("Categorical (5)", "hotel · market segment · channel · agent · company",
          f"One-hot; under {NB['nb10']['min_bookings']} Train bookings or never seen in Train → one 'infrequent' column; hotel → one 0/1 column"),
         ("Counts (2) and flag (1)", "previous cancellations · previous stays · repeat guest", "Counts: log(1 + count), then scaled with Train's mean and spread; flag kept as 0/1"),
         (f"{NB['nb10']['checks']} leakage checks passed", f"{NB['nb10']['columns']} columns, fitted on Train only",
          "No outcome column; Train-only statistics; label not used; rows independent; test never opened")]
for i, (head, cols, body) in enumerate(cards):
    y = 2.3 + i * 1.5
    rect(s, 0.6, y, 5.5, 1.35, TINT, radius=0.05)
    text(s, 0.85, y + 0.12, 5.0, 0.35, head, size=16, bold=True)
    text(s, 0.85, y + 0.48, 5.0, 0.3, cols, size=12, color=ORANGE, bold=True)
    text(s, 0.85, y + 0.8, 5.0, 0.5, body, size=12, color=MUTED)
rows = [["Model (notebook 11)", "Settings, fixed in advance"],
        ["Flat rule (reference)", "Each hotel's Train cancellation rate"],
        ["Logistic regression", "C = 1, up to 2,000 iterations"],
        ["Random forest", "300 trees, at least 20 bookings per leaf"],
        ["XGBoost", "300 rounds, depth 4, rate 0.05, 80% rows/columns"],
        ["CatBoost", "300 rounds, depth 4, rate 0.05"],
        ["All models", "Seed 0; no class weights or resampling"],
        ["Oversell rule", "Round expected cancellations down, subtract buffer"],
        ["Buffer choice", "Cheapest within 10 walks per 1,000 on Choose"]]
table(s, 6.45, 2.3, 6.3, rows, [1.95, 4.35], row_h=0.48, size=12, align=[L, L])

# ============================================================ 7. Training (notebook 11)
s = frame("6 · Training", "How well did the four models fit the training data?",
          "All four beat the flat rate by a similar margin on Train; these are in-sample numbers, so nothing was chosen here",
          "notebooks/11_train_models.ipynb · data/models/train_scores.csv · train_nightly_scores.csv (Train, Jul 2015 – Jun 2016)",
          "Notebook 11 fits each model on Train and scores it on the same Train bookings, so the numbers flatter the flexible models and no choice is made "
          "from them. All four improve on the flat hotel rate by a similar amount: log loss about 0.46 against 0.64, ROC AUC about 0.81 against 0.58, and "
          "the nightly count error about 6.2–6.5 rooms against 9.7. Logistic regression fits the nightly counts best in-sample. The tree models lean heavily "
          "on previous_cancellations, a provisional input: setting it to zero for the bookings that have one cuts their predicted probability from about 95% to "
          "under 40% for every model (notebook 13).")
rows = [["Model (in-sample, Train)", "Log loss ↓", "Brier ↓", "ROC AUC ↑", "Nightly error (rooms) ↓"]]
for mdl in [FL, LR_, RF_, XG, CB]:
    t = TR[mdl]
    rows.append([LABEL[mdl], f"{t['log_loss']:.3f}", f"{t['brier']:.3f}", f"{t['auc']:.3f}", f"{t['mae']:.2f}"])
table(s, 0.6, 2.35, 8.0, rows, [2.8, 1.2, 1.1, 1.2, 1.7], row_h=0.55, size=13)
rect(s, 8.95, 2.35, 3.8, 3.3, TINT, radius=0.04)
text(s, 9.2, 2.5, 3.3, 0.35, "Read with care", size=17, font=HEAD, bold=True)
text(s, 9.2, 2.95, 3.35, 2.6, ["Scored on the same bookings the models learnt from.",
                               "The real test of each model is the validation period (next slide).",
                               "Nightly error: average gap between expected and actual cancellations per hotel-night."],
     size=13, color=MUTED, space_after=8)
text(s, 0.6, 5.85, 12.15, 0.8, [[("Flat rule: ", {"bold": True}), (f"City {NB['flat_rates']['City Hotel']:.1%} and Resort {NB['flat_rates']['Resort Hotel']:.1%} — each hotel's Train cancellation rate, given to every booking. "
                                                                 "It is the client's current rule and the benchmark every model must beat.", {})]], size=13, color=MUTED)

# ============================================================ 8. Validation (notebook 12)
s = frame("7 · Validation", "How did the models do on nights they had not seen?",
          f"They lost much of their skill and predicted about 28% cancellations against an actual {VA[CB]['actual']:.1%} — 11 rooms too few per City night",
          "notebooks/12_validate_models.ipynb · 13_validation_results_explained.ipynb · data/models/val_scores.csv · val_nightly_scores.csv (Choose, Jul–Dec 2016)",
          "Notebook 12 runs the frozen Train models on the validation period without refitting. ROC AUC falls from about 0.82 to 0.70–0.71 for every model "
          "and log loss from about 0.46 to 0.60. All four predict too few cancellations: about 28% against an actual 36.9%, roughly 11 rooms too few per "
          "City Hotel night and 3 per Resort night. Notebook 13 traced the cause: bookings with a prior cancellation were 11.8% of Train (96.7% of them "
          "cancelled) but only 1.3% of the validation period, while everyone else cancelled more (27.6% → 36.4%). The flat rule's level stayed right because "
          "the hotels' rates barely moved.")
rows = [["Model", "ROC AUC  Train → val", "Log loss  Train → val", "Predicted rate (actual 36.9%)", "City nightly bias"]]
for mdl in [FL, LR_, RF_, XG, CB]:
    v, t = VA[mdl], TR[mdl]
    rows.append([LABEL[mdl], f"{t['auc']:.3f} → {v['auc']:.3f}", f"{t['log_loss']:.3f} → {v['log_loss']:.3f}", f"{v['mean_pred']:.1%}", f"{v['bias_city']:+.1f} rooms"])
table(s, 0.6, 2.35, 8.6, rows, [2.35, 1.6, 1.6, 1.75, 1.3], row_h=0.55, size=13)
rect(s, 9.5, 2.35, 3.25, 3.3, INK, radius=0.04)
text(s, 9.75, 2.5, 2.8, 0.3, "WHY", size=11, color=ORANGE, bold=True)
text(s, 9.75, 2.85, 2.8, 0.6, f"{DATA['prior_cancellation_share']['Train']:.1%} → {DATA['prior_cancellation_share']['Choose']:.1%}", size=28, font=HEAD, bold=True, color=PAPER)
text(s, 9.75, 3.5, 2.8, 2.1, "of bookings had a prior cancellation, Train vs validation. The models learnt 'prior cancellation = will cancel'; that signal nearly vanished.",
     size=12, color="C9D2DA")
text(s, 0.6, 5.85, 12.15, 0.8, "Bias = expected minus actual cancellations per night; below zero means too few expected. A steady bias can be absorbed by a smaller buffer; "
     "night-to-night swings cannot.", size=13, color=MUTED)

# ============================================================ 9. Buffers and costs (notebooks 12-13)
s = frame("8 · Buffers and costs", "Which method cost least within the walk limit?",
          "With a fair buffer per hotel, CatBoost was only 1.4% cheaper than the flat rule — and not reliably",
          "notebooks/12_validate_models.ipynb, 13_validation_results_explained.ipynb · data/models/val_results.csv · presentation/deck_data.py (per-hotel recomputation)",
          "Each method's oversell count is its expected cancellations rounded down, minus a buffer chosen as the cheapest that keeps the group within 10 walks per "
          "1,000 on the validation period. With one buffer for both hotels every model beat the flat rule by 11–16% — but mostly because the flat rule needed 16 "
          "rooms everywhere to protect the City Hotel, far too many at the Resort, while the models' under-prediction quietly gave the City Hotel extra "
          "protection. Notebook 13 gave every method a buffer per hotel: the flat rule dropped to €1.95M and CatBoost was only 1.4% cheaper, XGBoost 1.0%, "
          "while random forest and logistic regression cost more. Resampling the 27 validation weeks, CatBoost was cheaper in 74% of resamples and in 3 of 6 "
          "months — not a reliable difference.")
rows = [["Method", "One buffer: rooms", "Cost", "vs flat", "Per-hotel buffer: City / Resort", "Cost", "vs flat"]]
flat_shared, flat_ph = EV[FL]["shared_cost"], EVH[FL]["cost"]
for mdl in [FL, LR_, RF_, XG, CB]:
    e, ph = EV[mdl], EVH[mdl]
    rows.append([LABEL[mdl], e["shared_buffer"], m(e["shared_cost"]), "—" if mdl == FL else pct(e["shared_cost"], flat_shared),
                 f"{ph['city']} / {ph['resort']}", m(ph["cost"]), "—" if mdl == FL else pct(ph["cost"], flat_ph)])
hl = row_highlight(5, 7)
table(s, 0.6, 2.35, 12.15, rows, [2.55, 1.65, 1.35, 1.2, 2.7, 1.4, 1.3], row_h=0.5, size=13, highlight=hl)
rs = NB["resample_cheaper_than_flat"]
for i, (value, label) in enumerate([("16 rooms", "the flat rule's shared buffer: set by the City Hotel, wasted at the Resort"),
                                    (f"{rs[CB]:.0%}", "of resampled weeks in which CatBoost (per-hotel) cost less than the flat rule"),
                                    (f"{NB['months_cheaper_than_flat'][CB]} of 6", "validation months in which CatBoost (per-hotel) was cheaper")]):
    x = 0.6 + i * 4.1
    text(s, x, 5.55, 3.85, 0.55, value, size=26, font=HEAD, bold=True, color=ORANGE if i else INK)
    text(s, x, 6.12, 3.85, 0.7, label, size=12, color=MUTED)

# ============================================================ 10. The choice (notebook 13)
s = frame("9 · The choice", "Why was CatBoost chosen, and what was frozen?",
          "Lowest validation cost within the walk limit under both buffer setups — frozen with per-hotel buffers before any test result",
          "notebooks/13_validation_results_explained.ipynb · models/frozen_choice.json (frozen 2026-11-18 01:57:07) · docs/DECISIONS.md",
          "The selection rule was set before any result: lowest validation-period cost within the walk limit. CatBoost was first under both buffer setups, "
          f"and cheaper than XGBoost in {NB['catboost_vs_xgboost']}% of resamples, though only by about €7,000 — XGBoost would have been equally defensible. "
          "Logistic regression and random forest were out: with per-hotel buffers both cost more than the flat rule. The freeze, written before any test file "
          "was opened, fixed CatBoost as fitted on Train with buffers City 6 and Resort 3, and the benchmark: the flat rule with Train hotel rates and buffers "
          "City 20 and Resort 4. Caveats noted at the time: the edge was not reliable (74% of resamples), and if the client required each hotel separately to "
          "stay within 10 per 1,000, the flat rule would have been the cheapest method.")
for i, (label, head, body, dark) in enumerate([
        ("Chosen model", "CatBoost, buffers City 6 / Resort 3", f"Cheapest within the limit on validation: {m(EVH[CB]['cost'])}, {EVH[CB]['walks_per_1000']:.2f} walks per 1,000", True),
        ("Benchmark", "Flat rule, buffers City 20 / Resort 4", f"Hotel rates from Train (City {NB['flat_rates']['City Hotel']:.1%}, Resort {NB['flat_rates']['Resort Hotel']:.1%}): " f"{m(EVH[FL]['cost'])}, {EVH[FL]['walks_per_1000']:.2f} per 1,000", False)]):
    y = 2.35 + i * 1.6
    rect(s, 0.6, y, 6.0, 1.4, INK if dark else TINT, radius=0.05)
    text(s, 0.85, y + 0.15, 5.5, 0.3, label.upper(), size=11, color=ORANGE, bold=True)
    text(s, 0.85, y + 0.45, 5.5, 0.4, head, size=18, font=HEAD, bold=True, color=PAPER if dark else INK)
    text(s, 0.85, y + 0.9, 5.5, 0.45, body, size=12, color="C9D2DA" if dark else MUTED)
rect(s, 6.95, 2.35, 5.8, 3.0, TINT, radius=0.04)
text(s, 7.2, 2.5, 5.3, 0.35, "Known risks at the time of the choice", size=16, font=HEAD, bold=True)
text(s, 7.2, 2.95, 5.35, 2.4, [
    [("Not reliable: ", {"bold": True}), (f"cheaper than the flat rule in only {rs[CB]:.0%} of resampled weeks.", {})],
    [("Close call: ", {"bold": True}), (f"XGBoost within about €7,000; CatBoost cheaper in {NB['catboost_vs_xgboost']}% of resamples.", {})],
    [("Depends on the limit: ", {"bold": True}), ("if each hotel had to stay within 10 per 1,000, the flat rule was cheapest.", {})],
    [("Under-prediction: ", {"bold": True}), ("about 11 rooms too few per City night on validation.", {})]], size=12, color=MUTED, space_after=6)
text(s, 0.6, 5.65, 12.15, 1.1, [[("Frozen before any test file was opened: ", {"bold": True}),
                                  ("the method, both sets of buffers, the rule and the benchmark, with fingerprints of the model and preprocessor files (models/frozen_choice.json). "
                                   "The test notebook refuses to run if any of them change.", {})]], size=13, color=MUTED)

# ============================================================ 11. Test run 1 (notebook 14)
c1, f1 = R1[("City Hotel", "CatBoost")], R1[("City Hotel", "flat rule")]
c2, f2 = R1[("Resort Hotel", "CatBoost")], R1[("Resort Hotel", "flat rule")]
s = frame("10 · Test run 1", "What happened on the 2017 test?",
          f"CatBoost cost {eur(CAT1['cost (EUR)'] - FLAT1['cost (EUR)'])} more than the flat rule; both stayed within the walk limit — no saving",
          "notebooks/14_test_run.ipynb · data/models/test_results_primary.csv · test_accuracy.csv (2017 test, run once with the frozen settings)",
          f"Notebook 14 checked the frozen files, predicted the test bookings, saved the predictions, and only then opened the outcomes. CatBoost cost "
          f"{eur(CAT1['cost (EUR)'])} against {eur(FLAT1['cost (EUR)'])} for the flat rule — {eur(CAT1['cost (EUR)'] - FLAT1['cost (EUR)'])} more — with "
          f"{CAT1['walks per 1,000']:.2f} walks per 1,000 against {FLAT1['walks per 1,000']:.2f}; both within the limit. It was slightly cheaper at the City Hotel "
          f"and much dearer at the Resort, and cheaper in only {NB['run1']['months']} months. Accuracy at a 50% cut-off was "
          f"{NB['run1']['accuracy']['test|CatBoost']:.1%} against {NB['run1']['nobody_cancels']:.1%} for predicting that nobody cancels; ROC AUC "
          f"{NB['run1']['auc_test']:.3f}. The model predicted 27% cancellations against 39% actual: the under-prediction seen on validation got worse.")
rows = [["2017 test", "Cost", "Empty rooms", "Walked", "Per 1,000", "Limit"],
        ["Flat rule, 20 / 4", eur(FLAT1["cost (EUR)"]), f"{FLAT1['empty rooms']:,}", FLAT1["walked guests"], f"{FLAT1['walks per 1,000']:.2f}", "Met"],
        ["CatBoost, 6 / 3", eur(CAT1["cost (EUR)"]), f"{CAT1['empty rooms']:,}", CAT1["walked guests"], f"{CAT1['walks per 1,000']:.2f}", "Met"],
        ["  City: flat / CatBoost", f"{m(f1['cost (EUR)'])} / {m(c1['cost (EUR)'])}", "", "", f"{f1['walks per 1,000']:.2f} / {c1['walks per 1,000']:.2f}", ""],
        ["  Resort: flat / CatBoost", f"{m(f2['cost (EUR)'])} / {m(c2['cost (EUR)'])}", "", "", f"{f2['walks per 1,000']:.2f} / {c2['walks per 1,000']:.2f}", ""]]
hl = row_highlight(1, 6)
hl[(1, 5)] = (PEACH, GOOD, True)
hl[(2, 5)] = (TINT, GOOD, True)
table(s, 0.6, 2.35, 8.3, rows, [2.4, 1.85, 1.15, 0.85, 1.25, 0.8], row_h=0.55, size=13, highlight=hl)
for i, (value, label) in enumerate([(f"+{eur(CAT1['cost (EUR)'] - FLAT1['cost (EUR)'])}", "CatBoost over the flat rule"),
                                    (NB["run1"]["months"], "test months in which CatBoost was cheaper"),
                                    (f"{NB['run1']['accuracy']['test|CatBoost']:.1%}", f"accuracy; predicting 'nobody cancels' scores {NB['run1']['nobody_cancels']:.1%}")]):
    y = 2.35 + i * 1.35
    text(s, 9.3, y, 3.45, 0.55, value, size=26, font=HEAD, bold=True, color=CRIT if i == 0 else INK)
    text(s, 9.3, y + 0.58, 3.45, 0.6, label, size=12, color=MUTED)
text(s, 0.6, 5.35, 8.3, 1.4, [[("Why: ", {"bold": True}), ("the model expected 27% cancellations against 39% actual, so it oversold too little on most nights; "
                                                           "the buffers chosen on validation could not correct a gap that grew.", {})]], size=13, color=MUTED)

# ============================================================ 12. Retrained run 3 (notebooks 15-16)
s = frame("11 · Retraining", "Did retraining on more data fix it?",
          "Refitted on Train + validation, CatBoost and XGBoost cost less but walked 13 guests per 1,000 — over the limit, so rejected",
          "notebooks/15_retrain_train_val.ipynb, 16_final_test_run.ipynb · data/models/test_run3_results_primary.csv · models/frozen_choice_run3_train_val.json",
          "Disclosure first: this run was decided after run 1's result had been seen, so it is reported beside run 1, not instead of it, as the contract "
          "requires. (Run 2, XGBoost fitted on Train only, was frozen but never run.) Notebook 15 refitted the preprocessing and both models on Train plus "
          f"validation — {NB['run3']['columns']} encoded columns — and kept the validation buffers, because no unseen data was left to choose new ones. The refitted "
          f"models expected about {NB['run3']['shift']['CatBoost / City Hotel']:.0f} more cancellations per City night, so the same buffers oversold more. On the test "
          f"they cost {m(CAT3['cost (EUR)'])} (CatBoost) and {m(XGB3['cost (EUR)'])} (XGBoost), but walked {CAT3['walks per 1,000']:.2f} and "
          f"{XGB3['walks per 1,000']:.2f} per 1,000. The contract rejects any rule over 10, whatever it saves. A flat rule with Train + validation rates stayed "
          f"within the limit ({FLAT3F['walks per 1,000']:.2f}). A later, separate re-check in notebooks/pipeline also kept the flat rule (docs/PIPELINE_VALIDATION.md).")
rows = [["Run", "Method", "Cost", "Walks per 1,000", "Limit"],
        ["1 · frozen first", "Flat rule, 20 / 4", eur(FLAT1["cost (EUR)"]), f"{FLAT1['walks per 1,000']:.2f}", "Met"],
        ["1 · frozen first", "CatBoost, Train fit", eur(CAT1["cost (EUR)"]), f"{CAT1['walks per 1,000']:.2f}", "Met"],
        ["2", "XGBoost, Train fit", "not run", "—", "Superseded"],
        ["3 · after run 1", "CatBoost, Train + val fit", eur(CAT3["cost (EUR)"]), f"{CAT3['walks per 1,000']:.2f}", "Breached"],
        ["3 · after run 1", "XGBoost, Train + val fit", eur(XGB3["cost (EUR)"]), f"{XGB3['walks per 1,000']:.2f}", "Breached"],
        ["3 · fairness check", "Flat rule, Train + val rates", eur(FLAT3F["cost (EUR)"]), f"{FLAT3F['walks per 1,000']:.2f}", "Met"]]
hl = {(r, 4): ((TINT if r % 2 == 0 else PAPER), GOOD, True) for r in (1, 2, 6)}
hl.update({(r, 4): ((TINT if r % 2 == 0 else PAPER), CRIT, True) for r in (4, 5)})
table(s, 0.6, 2.35, 8.3, rows, [1.85, 2.6, 1.45, 1.35, 1.05], row_h=0.5, size=13, highlight=hl, align=[L, L, R, R, L])
rect(s, 9.2, 2.35, 3.55, 3.5, TINT, radius=0.04)
text(s, 9.45, 2.5, 3.1, 0.3, "WHY THE WALKS ROSE", size=11, color=ORANGE, bold=True)
text(s, 9.45, 2.85, 3.1, 0.6, f"+{NB['run3']['shift']['CatBoost / City Hotel']:.1f} rooms", size=28, font=HEAD, bold=True)
text(s, 9.45, 3.5, 3.1, 2.3, "more expected cancellations per City night after refitting, with the buffers unchanged: the models oversold more, cutting empty rooms "
     "but walking more guests.", size=12, color=MUTED)
text(s, 0.6, 6.0, 12.15, 0.75, "Choosing a bigger buffer now, after seeing these results, would be tuning on the test period — not allowed.", size=13, color=MUTED, italic=True)

exec((Path(__file__).parent / "deck_leads.py").read_text(encoding="utf-8"))  # slides 13-17: decisions by lead

# ============================================================ 18. Conclusion (dark)
s = prs.slides.add_slide(BLANK)
rect(s, 0, 0, 13.333, 7.5, INK)
text(s, 0.6, 0.45, 8, 0.28, "17 · CONCLUSION AND NEXT STEPS", size=11, color=ORANGE, bold=True)
text(s, 0.6, 0.8, 12.1, 0.7, "So what should the hotels do?", size=30, font=HEAD, bold=True, color=PAPER)
text(s, 0.6, 1.55, 12.1, 0.5, "Keep the flat rule with a separate margin per hotel; no model beat it within the walk limit on the 2017 test", size=17, color="B8C2CB")
cols = [("What the evidence shows", [f"Flat rule (City 20, Resort 4): {m(FLAT1['cost (EUR)'])}, {FLAT1['walks per 1,000']:.2f} per 1,000 — within the limit",
                                     f"CatBoost, frozen first: {eur(CAT1['cost (EUR)'] - FLAT1['cost (EUR)'])} more",
                                     "Refitted models: cheaper, but 13 walks per 1,000 — rejected",
                                     "Models under-predicted because a key input (prior cancellations) shifted between periods"]),
        ("Proposed next steps", ["Get timestamped booking snapshots from the hotels' system",
                                 "Confirm the provisional inputs' timing, or drop prior cancellations",
                                 "Run the flat rule beside the revenue manager on new nights",
                                 "Try models again only on unseen nights, with live data"])]
for i, (head, lines) in enumerate(cols):
    x = 0.6 + i * 6.15
    text(s, x, 2.45, 5.9, 0.4, head, size=19, font=HEAD, bold=True, color=ORANGE if i else PAPER)
    for j, line in enumerate(lines):
        y = 3.05 + j * 0.85
        oval(s, x, y + 0.08, 0.16, ORANGE if i else "C9D2DA")
        text(s, x + 0.35, y, 5.5, 0.75, line, size=15, color="DDE3E8")
text(s, 0.6, 6.55, 12.1, 0.4, "Limits: booking rows stand in for rooms, euros are simulated, there are no records of real walks, and the 2017 period was scored "
     "more than once. Next steps are proposals; docs/ROADMAP.md is blank.", size=12, color="9AA6B1", italic=True)
s.notes_slide.notes_text_frame.text = (
    "Conclusion. The client asked for a better rule than its flat rule, proved in euros. Our best model, CatBoost, was chosen fairly on the validation "
    f"period and frozen before the test; on January–August 2017 it cost {eur(CAT1['cost (EUR)'] - FLAT1['cost (EUR)'])} more than the flat rule with "
    "separate margins per hotel, which stayed within the walk limit. Refitting on more data made the models cheaper only by breaking the limit, so the "
    "contract rejects them. The honest recommendation is to keep the flat rule, with a margin per hotel, and to revisit models once timestamped booking "
    "snapshots exist. Limits: the data has booking rows, not rooms; euros are simulated; there are no records of real walks; and the test period was scored "
    "more than once, so every run is reported.")
