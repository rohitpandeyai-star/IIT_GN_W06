"""Collect every number the presentation shows into presentation/deck_data.json.

Reads only repository evidence (notebooks/pipeline outputs under evidence/) and the supplied data
and contract. The few figures it derives itself (the frozen rule's 14-night table and the Choose-only
sensitivity runs) use src/contract.py unchanged. Run from the repository root:

    python presentation/deck_data.py
"""
import json
import math
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
import contract  # noqa: E402
import data  # noqa: E402

E = ROOT / "evidence"
out = {}

# ---- Data facts (data/hotels.csv, all periods; descriptive only)
df = data.read_raw()
df["arrival_date"] = data.arrival_date(df)
df["nights"] = df["stays_in_weekend_nights"] + df["stays_in_week_nights"]
by_hotel = df.groupby("hotel")["is_canceled"].agg(["size", "sum", "mean"])
non_refund = df[df["deposit_type"] == "Non Refund"]
train, choose, proof = contract.split_periods(df)
monthly = (df.assign(month=df["arrival_date"].dt.to_period("M").astype(str))
             .groupby(["month", "hotel"])["is_canceled"].mean().unstack())
out["data"] = {
    "rows": len(df), "columns": int(df.shape[1] - 1), "first_arrival": str(df["arrival_date"].min().date()),
    "last_arrival": str(df["arrival_date"].max().date()), "cancelled": int(df["is_canceled"].sum()),
    "cancel_rate": float(df["is_canceled"].mean()),
    "hotels": {h: {"bookings": int(r["size"]), "cancelled": int(r["sum"]), "rate": float(r["mean"])} for h, r in by_hotel.iterrows()},
    "non_refund": {"bookings": len(non_refund), "cancelled": int(non_refund["is_canceled"].sum()),
                   "rate": float(non_refund["is_canceled"].mean())},
    "exact_duplicate_rows": int(df.drop(columns=["arrival_date", "nights"]).duplicated().sum()),
    "periods": {"Train": len(train), "Choose": len(choose), "Proof": len(proof)},
    "period_rates": {"Train": float(train["is_canceled"].mean()), "Choose": float(choose["is_canceled"].mean())},
    "prior_cancellation_share": {"Train": float((train["previous_cancellations"] > 0).mean()),
                                 "Choose": float((choose["previous_cancellations"] > 0).mean())},
    "monthly_rate": {"months": list(monthly.index), "City Hotel": monthly["City Hotel"].round(4).tolist(),
                     "Resort Hotel": monthly["Resort Hotel"].round(4).tolist()},
}

# ---- Baselines and models on Choose (notebooks 06, 07, 08, 09)
b06 = pd.read_csv(E / "baselines_pooling/choose_booking_metrics.csv").set_index("method")
n06 = pd.read_csv(E / "baselines_pooling/choose_nightly_metrics.csv").set_index("method")
b07 = pd.read_csv(E / "train_model_experiments/choose_booking_metrics.csv").set_index("model")
n07 = pd.read_csv(E / "train_model_experiments/choose_nightly_metrics.csv").set_index("model")
t08 = pd.read_csv(E / "hyperparameter_experiments/choose_tuned_comparison.csv").set_index("model")
cal = json.loads((E / "probability_calibration/calibration_decision.json").read_text())
mae = n06["mean_absolute_error_cancellations"]
out["model_matrix"] = [
    {"method": "Global rate", "brier": b06.loc["global", "brier_score"], "log_loss": b06.loc["global", "log_loss"], "auc": None, "mae": mae["global"]},
    {"method": "Hotel rate", "brier": b06.loc["hotel_specific", "brier_score"], "log_loss": b06.loc["hotel_specific", "log_loss"], "auc": None, "mae": mae["hotel_specific"]},
    {"method": "Pooled rate (m = 100)", "brier": b06.loc["pooled_m_100", "brier_score"], "log_loss": b06.loc["pooled_m_100", "log_loss"], "auc": None, "mae": mae["pooled_m_100"]},
    {"method": "Dummy classifier", "brier": b07.loc["dummy", "brier_score"], "log_loss": b07.loc["dummy", "log_loss"], "auc": b07.loc["dummy", "roc_auc"], "mae": n07.loc["dummy", "mean_absolute_error_cancellations"]},
    {"method": "Logistic regression (C = 1)", "brier": b07.loc["logistic_regression", "brier_score"], "log_loss": b07.loc["logistic_regression", "log_loss"], "auc": b07.loc["logistic_regression", "roc_auc"], "mae": n07.loc["logistic_regression", "mean_absolute_error_cancellations"]},
    {"method": "Random forest (150, leaf 20)", "brier": b07.loc["random_forest", "brier_score"], "log_loss": b07.loc["random_forest", "log_loss"], "auc": b07.loc["random_forest", "roc_auc"], "mae": n07.loc["random_forest", "mean_absolute_error_cancellations"]},
    {"method": "Selected: logistic, C = 0.1", "brier": t08.loc["selected_tuned_model", "brier_score"], "log_loss": t08.loc["selected_tuned_model", "log_loss"], "auc": None, "mae": None},
    {"method": "Selected + calibration", "brier": cal["choose_brier_calibrated"], "log_loss": cal["choose_log_loss_calibrated"], "auc": None, "mae": None},
]
out["model_matrix"] = [{k: (None if v is None or (isinstance(v, float) and math.isnan(v)) else (float(v) if not isinstance(v, str) else v))
                        for k, v in r.items()} for r in out["model_matrix"]]

# ---- Chronological validation (notebook 08)
cs = pd.read_csv(E / "hyperparameter_experiments/candidate_summary.csv")
out["cv"] = [{"label": ("Logistic C=" + str(eval(s)["C"])) if m == "logistic_regression"
              else f"Forest {eval(s)['n_estimators']}/leaf {eval(s)['min_samples_leaf']}",
              "brier": float(b), "std": float(sd), "log_loss": float(ll)}
             for m, s, b, sd, ll in cs[["model", "settings", "mean_brier_score", "std_brier_score", "mean_log_loss"]].itertuples(index=False)]
dates = np.array(sorted(train["arrival_date"].unique()))
blocks = np.array_split(dates, 4)
out["folds"] = [{"fit": [str(pd.Timestamp(blocks[0][0]).date()), str(pd.Timestamp(blocks[k - 1][-1]).date())],
                 "validate": [str(pd.Timestamp(blocks[k][0]).date()), str(pd.Timestamp(blocks[k][-1]).date())]} for k in (1, 2, 3)]

# ---- Calibration (notebook 09)
rel = {}
for name in ["uncalibrated", "calibrated"]:
    t = pd.read_csv(E / f"probability_calibration/choose_{name}_reliability.csv")
    t = t[t["bookings"] > 0]
    rel[name] = {"predicted": t["mean_predicted_probability"].round(4).tolist(),
                 "observed": t["observed_cancellation_rate"].round(4).tolist(), "bookings": t["bookings"].astype(int).tolist()}
hcal = pd.read_csv(E / "probability_calibration/choose_hotel_calibration_metrics.csv")
probs = pd.read_csv(E / "probability_calibration/choose_calibrated_probabilities.csv", index_col=0)
out["calibration_means"] = {"uncalibrated": float(probs["uncalibrated"].mean()), "calibrated": float(probs["calibrated"].mean()),
                            "actual": float(probs["actual"].mean())}
out["calibration"] = {"decision": cal, "reliability": rel,
                      "hotel_brier": {f"{h}|{m}": float(b) for h, m, b in hcal[["hotel", "probability_method", "brier_score"]].itertuples(index=False)}}

# ---- Uncertainty (notebook 10)
iv = pd.read_csv(E / "uncertainty_conformal/choose_nightly_uncertainty_intervals.csv", parse_dates=["arrival_date"])
city = iv[iv["hotel"] == "City Hotel"].sort_values("arrival_date")
summ = pd.read_csv(E / "uncertainty_conformal/choose_interval_summary.csv")
hsumm = pd.read_csv(E / "uncertainty_conformal/choose_hotel_interval_summary.csv")
conf = pd.read_csv(E / "uncertainty_conformal/conformal_settings.csv").iloc[0]
out["uncertainty"] = {
    "city_series": {"dates": city["arrival_date"].dt.strftime("%d %b").tolist(), "actual": city["actual_cancellations"].astype(int).tolist(),
                    "expected": city["expected_cancellations"].round(2).tolist(), "normal_lower": city["normal_lower"].round(2).tolist(),
                    "normal_upper": city["normal_upper"].round(2).tolist(), "conformal_lower": city["conformal_lower"].round(2).tolist(),
                    "conformal_upper": city["conformal_upper"].round(2).tolist()},
    "summary": summ.to_dict("records"), "by_hotel": hsumm.to_dict("records"),
    "conformal": {"quantile": float(conf["conformal_residual_quantile"]), "nights": int(conf["calibration_nights"]),
                  "rank": int(conf["conformal_rank"])},
    "mean_spread_choose": float(iv["spread"].mean()),
}

# ---- Policies on Choose (notebook 11)
ps = pd.read_csv(E / "choose_policy_selection/choose_policy_scores.csv")
hp = pd.read_csv(E / "choose_policy_selection/choose_hotel_policy_scores.csv")
frozen = json.loads((E / "choose_policy_selection/frozen_configuration.json").read_text())


def family(p):
    if p.startswith("flat_rule_margin_"):
        return "Flat rule with margin"
    if p.startswith("model_margin_"):
        return "Model with margin"
    if p.startswith("model_buffer_") or p == "model_expected":
        return "Model + spread buffer (declared)"
    if p == "no_overbooking":
        return "No overbooking"
    return "Rate rules, no margin (declared)"


ps["family"] = ps["policy"].map(family)
out["policies"] = {
    "all": ps[["policy", "family", "cost_eur", "empty_rooms", "walked_guests", "walks_per_1000", "ceiling_met"]].to_dict("records"),
    "selected": frozen["selected_policy"], "model_benchmark": frozen["model_policy_benchmark"]["policy"],
    "hotel": hp[hp["policy"].isin([frozen["selected_policy"], frozen["model_policy_benchmark"]["policy"], "no_overbooking"])].to_dict("records"),
}
sweep = {}
for fam_prefix, key in [("flat_rule_margin_", "flat"), ("model_margin_", "model")]:
    s = ps[ps["policy"].str.startswith(fam_prefix)].copy()
    s["margin"] = s["policy"].str.replace(fam_prefix, "").astype(int)
    s = s.sort_values("margin")
    sweep[key] = {"margin": s["margin"].tolist(), "cost": s["cost_eur"].round(0).tolist(), "walks_per_1000": s["walks_per_1000"].tolist()}
out["sweep"] = sweep

# Worked example night (Choose): the selected-policy nightly table from notebook 11.
nights = pd.read_csv(E / "choose_policy_selection/choose_selected_policy_nights.csv", parse_dates=["arrival_date"])
rates = frozen["flat_rule_benchmark"]["hotel_rates_from_train"]
ex = nights[(nights["hotel"] == "City Hotel") & (nights["arrival_date"] == pd.Timestamp("2016-10-14"))].iloc[0]
flat_expected = rates["City Hotel"] * ex["book"]
out["example_night"] = {"hotel": "City Hotel", "date": "2016-10-14", "bookings": int(ex["book"]),
                        "model_expected": float(ex["expected"]), "model_spread": float(ex["spread"]),
                        "flat_rate": rates["City Hotel"], "flat_expected": float(flat_expected),
                        "flat_k": int(ex["oversell_count"]), "model_margin_k": int(max(math.ceil(ex["expected"]) - 18, 0)),
                        "actual_cancelled": int(ex["cancelled"]), "stay_value": float(ex["stay_value"])}

# ---- Proof (notebook 12)
pg = pd.read_csv(E / "proof_evaluation/proof_group_score.csv").iloc[0]
ph = pd.read_csv(E / "proof_evaluation/proof_hotel_scores.csv")
pb = pd.read_csv(E / "proof_evaluation/proof_benchmark_comparison.csv")
out["proof"] = {"group": pg.to_dict(), "hotels": ph.to_dict("records"), "benchmarks": pb.to_dict("records")}

# ---- Choose-only sensitivity (illustrative; not selection candidates; contract unchanged)
cal_p = pd.read_csv(E / "probability_calibration/choose_calibrated_probabilities.csv", index_col=0).loc[choose.index, "calibrated"]
scoring = choose[["hotel", "arrival_date", "is_canceled", "adr", "nights"]]
model_nt = contract.nightly_table(scoring, cal_p.to_numpy())
flat_nt = contract.nightly_table(scoring, choose["hotel"].map(rates).to_numpy())


def score(nt, k, walk_cost=contract.WALK_COST):
    k = pd.Series(np.asarray(k, dtype=float), index=nt.index)
    empty = (nt["cancelled"] - k).clip(lower=0)
    walks = (k - nt["cancelled"]).clip(lower=0)
    arrivals = (nt["book"] - nt["cancelled"]).sum()
    return {"cost": float((empty * nt["stay_value"]).sum() + (walks * walk_cost).sum()), "empty": int(empty.sum()),
            "walks": int(walks.sum()), "walks_per_1000": float(1000 * walks.sum() / arrivals)}


# Check the recomputation reproduces notebook 11 exactly before using it.
check = score(flat_nt, np.maximum(np.ceil(flat_nt["expected"]) - 17, 0))
assert abs(check["cost"] - frozen["choose_scores"]["selected"]["cost_eur"]) < 0.5, check
uncert = []
for label, k in [("Expected count, no buffer", np.ceil(model_nt["expected"])),
                 ("Normal 90% lower bound (E − 1.645·sd)", np.floor(np.maximum(model_nt["expected"] - 1.645 * model_nt["spread"], 0))),
                 ("Normal 99% lower bound (E − 2.326·sd)", np.floor(np.maximum(model_nt["expected"] - 2.326 * model_nt["spread"], 0))),
                 (f"Conformal 90% lower bound (E − {out['uncertainty']['conformal']['quantile']:.1f})",
                  np.floor(np.maximum(model_nt["expected"] - out["uncertainty"]["conformal"]["quantile"], 0))),
                 ("Fixed margin of 18 rooms (Choose-selected)", np.maximum(np.ceil(model_nt["expected"]) - 18, 0))]:
    uncert.append({"rule": label, **score(model_nt, k)})
walk_cost = []
for w in [150, 300, 600, 1000]:
    best = None
    for m in range(0, 61):
        r = score(flat_nt, np.maximum(np.ceil(flat_nt["expected"]) - m, 0), walk_cost=w)
        if r["walks_per_1000"] <= contract.WALK_CEILING and (best is None or r["cost"] < best["cost"]):
            best = {"walk_cost": w, "margin": m, **r}
    walk_cost.append(best)
out["sensitivity"] = {"uncertainty_buffers": uncert, "walk_cost": walk_cost, "model_mean_spread": float(model_nt["spread"].mean())}

# ---- The revenue manager's table: frozen rule applied to the final book, 18-31 Aug 2017 (historical replay)
window = df[(df["arrival_date"] >= "2017-08-18") & (df["arrival_date"] <= "2017-08-31")]
counts = window.groupby(["arrival_date", "hotel"]).size().unstack(fill_value=0)
margin = frozen["selected_policy_rule"]["margin"]
table = []
for d, row in counts.iterrows():
    entry = {"date": d.strftime("%a %d %b")}
    for h in ["City Hotel", "Resort Hotel"]:
        exp = rates[h] * row[h]
        entry[h] = {"bookings": int(row[h]), "expected": round(exp, 1), "oversell": int(max(math.ceil(exp) - margin, 0))}
    table.append(entry)
out["fourteen_nights"] = table

# ---- Engineering evidence
manifest = json.loads((E / "pipeline_run/run_manifest.json").read_text())
check_list = pd.read_csv(E / "nightly_pipeline_validation/validation_checklist.csv")
smoke = json.loads((E / "nightly_pipeline_validation/smoke_test.json").read_text())
out["engineering"] = {"notebooks": {k: v["cells_with_errors"] for k, v in manifest["notebooks"].items()},
                      "tests": manifest["tests"], "environment": manifest["environment"], "data_sha256": manifest["data"]["sha256"],
                      "checklist": check_list.to_dict("records"), "smoke_return_code": smoke["return_code"],
                      "artifact_schema": smoke["artifact_schema"], "approved_schema": smoke["approved_schema"]}
bench = pd.read_csv(E / "expanded_benchmark/proof_audit_all_models.csv")
out["benchmark"] = {"configurations": 27, "completed": 26, "proof_rows": len(bench),
                    "proof_breached": int((~bench["ceiling_met"].astype(bool)).sum())}


# ---- Cleaning facts, recomputed from the raw file (decisions C1-C6 in notebooks/05_apply_cleaning_decisions.ipynb)
raw = data.read_raw()
raw_train = raw[data.arrival_date(raw) < contract.TRAIN_END]
deduped = raw_train.drop_duplicates()
out["cleaning"] = {
    "meal_undefined": int((raw["meal"] == "Undefined").sum()),
    "agent_missing": int(raw["agent"].isna().sum()), "company_missing": int(raw["company"].isna().sum()),
    "country_missing": int(raw["country"].isna().sum()), "children_missing": int(raw["children"].isna().sum()),
    "children_zero_share_train": float((raw_train["children"] == 0).mean()),
    "train_rate_all_rows": float(raw_train["is_canceled"].mean()), "train_rate_without_repeats": float(deduped["is_canceled"].mean()),
    "train_rows_without_repeats": len(deduped),
}
assert out["cleaning"]["meal_undefined"] == 1169 and out["cleaning"]["agent_missing"] == 16340  # as logged in notebook 05

# ---- Column decisions, read from notebook 06's decision cells (as notebook 07 does)
nb06 = json.loads((ROOT / "notebooks" / "06_forecast_column_selection.ipynb").read_text(encoding="utf-8"))
decisions = {}
for cell in nb06["cells"]:
    if cell.get("id", "").startswith("decide-"):
        exec("".join(cell["source"]), {"my_decisions": decisions})
out["columns"] = {"counts": {u: sum(1 for d in decisions.values() if d["use"] == u) for u in ("input", "provisional input", "exclude")},
                  "tests": {c: d["tests"] for c, d in decisions.items()}, "use": {c: d["use"] for c, d in decisions.items()}}

# ---- Earlier experiments: notebooks 10-16 (LR, RF, XGBoost, CatBoost on the same 8 inputs)
MD = ROOT / "data" / "models"
vs = pd.read_csv(MD / "val_scores.csv").set_index("method")
vr = pd.read_csv(MD / "val_results.csv")
vr = vr[vr["hotel"] == "group"].set_index("method")
shared_buffers = json.loads((MD / "val_chosen_buffers.json").read_text())["chosen_buffers"]

# Notebook 13's per-hotel buffers (City, Resort), recomputed from the saved val probabilities.
val_p = pd.read_csv(MD / "val_probabilities.csv", index_col="row").loc[choose.index]
val_scoring = choose[["hotel", "arrival_date", "is_canceled", "adr", "nights"]]


def best_per_hotel(method):
    nt = contract.nightly_table(val_scoring, val_p[method].to_numpy())
    parts = {}
    for hotel in ["City Hotel", "Resort Hotel"]:
        t = nt.xs(hotel, level="hotel")
        e, a, v = np.floor(t["expected"].to_numpy()), t["cancelled"].to_numpy(), t["stay_value"].to_numpy()
        k = np.maximum(e[None, :] - np.arange(61)[:, None], 0)
        empty, walks = np.clip(a - k, 0, None), np.clip(k - a, 0, None)
        parts[hotel] = ((empty * v).sum(1) + contract.WALK_COST * walks.sum(1), walks.sum(1), (t["book"] - t["cancelled"]).sum())
    (cc, cw, ca), (rc, rw, ra) = parts["City Hotel"], parts["Resort Hotel"]
    cost = cc[:, None] + rc[None, :]
    rate = 1000 * (cw[:, None] + rw[None, :]) / (ca + ra)
    i, j = np.unravel_index(np.argmin(np.where(rate <= contract.WALK_CEILING, cost, np.inf)), cost.shape)
    return {"city": int(i), "resort": int(j), "cost": float(cost[i, j]), "walks_per_1000": float(rate[i, j])}


per_hotel = {m: best_per_hotel(m) for m in val_p.columns}
assert round(per_hotel["flat-rule reference"]["cost"]) == 1950066 and round(per_hotel["CatBoost"]["cost"]) == 1922977, per_hotel
runs = pd.read_csv(MD / "test_all_runs.csv")
run1 = pd.read_csv(MD / "test_results_primary.csv")
run1 = run1[run1["hotel"] == "group"].set_index("method")
out["earlier"] = {
    "val": {m: {"auc": float(vs.loc[m, "ROC AUC (val)"]), "brier": float(vs.loc[m, "Brier (val)"]), "log_loss": float(vs.loc[m, "log loss (val)"]),
                "shared_buffer": int(shared_buffers[m]), "shared_cost": float(vr.loc[m, "cost (EUR)"]),
                "shared_walks": float(vr.loc[m, "walks per 1,000"]), "per_hotel": per_hotel[m]} for m in vs.index},
    "proof_run1": {m: {"cost": float(r["cost (EUR)"]), "walks_per_1000": float(r["walks per 1,000"]),
                       "empty": int(r["empty rooms"]), "walked": int(r["walked guests"])} for m, r in run1.iterrows()},
    "proof_run3": {r["method"]: {"cost": float(r["cost (EUR)"]), "walks_per_1000": float(r["walks per 1,000"])}
                   for _, r in runs.iterrows() if str(r["run"]).startswith("3")},
}


# ---- Notebooks 10-16 in detail (the story the deck now follows)
def outputs_of(name):
    nb = json.loads((ROOT / "notebooks" / name).read_text(encoding="utf-8"))
    return "\n".join("".join(o.get("text") or "") for c in nb["cells"] if c["cell_type"] == "code" for o in c.get("outputs", []))


import re  # noqa: E402

ts = pd.read_csv(MD / "train_scores.csv").set_index("model")
tn = pd.read_csv(MD / "train_nightly_scores.csv")
tn = tn[tn["hotel"] == "group"].set_index("model")
vn = pd.read_csv(MD / "val_nightly_scores.csv")
vn_group = vn[vn["hotel"] == "group"].set_index("method")
vn_city = vn[vn["hotel"] == "City Hotel"].set_index("method")
acc1 = pd.read_csv(MD / "test_accuracy.csv")
acc3 = pd.read_csv(MD / "test_run3_accuracy.csv").set_index("Unnamed: 0")
r1 = pd.read_csv(MD / "test_results_primary.csv")
r3 = pd.read_csv(MD / "test_run3_results_primary.csv")
freeze1 = json.loads((ROOT / "models" / "frozen_choice.json").read_text())
freeze3 = json.loads((ROOT / "models" / "frozen_choice_run3_train_val.json").read_text())

# Notebook 13's week-resampling check, recomputed with its seed, for the per-hotel buffers.
dates = None
week_costs = {}
for m, ph in per_hotel.items():
    nt = contract.nightly_table(val_scoring, val_p[m].to_numpy())
    b = np.where(nt.index.get_level_values("hotel") == "City Hotel", ph["city"], ph["resort"])
    k = np.maximum(np.floor(nt["expected"].to_numpy()) - b, 0)
    cost = (nt["cancelled"] - k).clip(lower=0) * nt["stay_value"] + (k - nt["cancelled"]).clip(lower=0) * contract.WALK_COST
    d = nt.index.get_level_values("arrival_date")
    week_costs[m] = cost.groupby(d.to_period("W")).sum()
    if m == "flat-rule reference":
        flat_month = cost.groupby(d.month).sum()
    else:
        week_costs[m + "_months"] = cost.groupby(d.month).sum()
weekly = pd.DataFrame({m: v for m, v in week_costs.items() if not m.endswith("_months")})
draws = np.random.default_rng(0).integers(0, len(weekly), (4000, len(weekly)))
tot = {m: weekly[m].to_numpy()[draws].sum(axis=1) for m in weekly}
resample = {m: float((tot[m] < tot["flat-rule reference"]).mean()) for m in weekly if m != "flat-rule reference"}
months_cheaper = {m: int((week_costs[m + "_months"] < flat_month).sum()) for m in weekly if m != "flat-rule reference"}
assert round(100 * resample["CatBoost"]) == 74 and round(100 * resample["XGBoost"]) == 69, resample  # as notebook 13 reports

out["nb"] = {
    "nb10": {"checks": int(re.search(r"All (\d+) checks pass", outputs_of("10_preprocessing_leakage_checked.ipynb")).group(1)),
             "columns": len(json.loads((ROOT / "data/preprocessed/feature_names.json").read_text())["output_columns"]),
             "min_bookings": json.loads((ROOT / "data/preprocessed/feature_names.json").read_text())["min_bookings_per_category"]},
    "train": {m: {"log_loss": float(ts.loc[m, "log loss"]), "brier": float(ts.loc[m, "Brier score"]), "auc": float(ts.loc[m, "ROC AUC"]),
                  "mae": float(tn.loc[m, "mean absolute error (rooms)"])} for m in ts.index},
    "val": {m: {"log_loss": float(vs.loc[m, "log loss (val)"]), "auc": float(vs.loc[m, "ROC AUC (val)"]),
                "mean_pred": float(vs.loc[m, "mean predicted rate (val)"]), "actual": float(vs.loc[m, "actual rate (val)"]),
                "mae": float(vn_group.loc[m, "mean absolute error (rooms)"]), "bias": float(vn_group.loc[m, "mean error (rooms)"]),
                "bias_city": float(vn_city.loc[m, "mean error (rooms)"])} for m in vs.index},
    "flat_rates": freeze1["flat_rule_hotel_rates_from_train"],
    "resample_cheaper_than_flat": resample, "months_cheaper_than_flat": months_cheaper,
    "catboost_vs_xgboost": re.search(r"CatBoost cheaper than XGBoost in (\d+)%", outputs_of("13_validation_results_explained.ipynb")).group(1),
    "run1": {"rows": r1.to_dict("records"), "frozen_at": freeze1["frozen_at"],
             "accuracy": {f"{p}|{m}": float(a) for p, m, a in acc1[["Unnamed: 0", "Unnamed: 1", "accuracy (50% cut-off)"]].itertuples(index=False)},
             "auc_test": float(acc1[(acc1["Unnamed: 0"] == "test") & (acc1["Unnamed: 1"] == "CatBoost")]["ROC AUC"].iloc[0]),
             "nobody_cancels": float(acc1[acc1["Unnamed: 0"] == "test"]["accuracy of 'nobody cancels'"].iloc[0]),
             "months": re.search(r"cheaper than the flat rule in (\d+ of \d+) months", outputs_of("14_test_run.ipynb")).group(1)},
    "run3": {"rows": r3.to_dict("records"), "frozen_at": freeze3["frozen_at"], "shift": freeze3["val_expected_count_shift_rooms"],
             "columns": int(re.search(r"(\d+) prepared columns", outputs_of("15_retrain_train_val.ipynb")).group(1)),
             "auc": {m: float(acc3.loc[m, "ROC AUC"]) for m in ["CatBoost", "XGBoost"]}},
}

# ---- Lead-decision slides: does the walk ceiling bind, and what is the cost ratio? (notebook 12's sweep, validation only)
sweep = pd.read_csv(MD / "val_buffer_sweep.csv")
uncon = {}
for m, g in sweep.groupby("method"):
    best, ok = g.loc[g["cost_eur"].idxmin()], g[g["ceiling_met"]]
    chosen = ok.loc[ok["cost_eur"].idxmin()]
    uncon[m] = {"buffer": int(best["buffer"]), "cost": float(best["cost_eur"]), "walks_per_1000": float(best["walks_per_1000"]),
                "chosen_buffer": int(chosen["buffer"]), "chosen_cost": float(chosen["cost_eur"])}
assert uncon["CatBoost"]["chosen_buffer"] == 5 and uncon["flat-rule reference"]["chosen_buffer"] == 16
nt_cb = contract.nightly_table(val_scoring, val_p["CatBoost"].to_numpy())
stay = {h: float(nt_cb.loc[h, "stay_value"].median()) for h in ["City Hotel", "Resort Hotel"]}
out["nb"]["leads"] = {"unconstrained": uncon, "median_stay_value": stay,
                      "critical_ratio": {h: v / (v + contract.WALK_COST) for h, v in stay.items()}}


def plain(o):
    if isinstance(o, dict):
        return {str(k): plain(v) for k, v in o.items()}
    if isinstance(o, (list, tuple)):
        return [plain(v) for v in o]
    if isinstance(o, (np.integer,)):
        return int(o)
    if isinstance(o, (np.floating,)):
        return None if np.isnan(o) else float(o)
    if isinstance(o, (np.bool_,)):
        return bool(o)
    if isinstance(o, float) and math.isnan(o):
        return None
    return o


(Path(__file__).parent / "deck_data.json").write_text(json.dumps(plain(out), indent=1), encoding="utf-8")
print("wrote presentation/deck_data.json")
print(json.dumps(plain({"example": out["example_night"], "uncert": out["sensitivity"]["uncertainty_buffers"],
                        "walk_cost": out["sensitivity"]["walk_cost"], "first_nights": out["fourteen_nights"][:3]}), indent=1))
