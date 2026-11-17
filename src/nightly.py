"""Frozen-model nightly cancellation and overbooking recommendation pipeline.

Example:
    python src/nightly.py --input data/hotels.csv --from 2017-08-18 --nights 14

This script performs inference only. It never fits, tunes, or recalibrates a model.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import platform
import sys
import uuid
from datetime import date
from pathlib import Path
from typing import Iterable

import joblib
import numpy as np
import pandas as pd
import sklearn
import xgboost

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(Path(__file__).resolve().parent))
from features import CATEGORICAL, FEATURE_COLUMNS, NUMERIC, make_features  # noqa: E402

EXPECTED_HOTELS = ("City Hotel", "Resort Hotel")
TARGET = "is_canceled"
DATE_PARTS = ("arrival_date_year", "arrival_date_month", "arrival_date_day_of_month")
NIGHT_PARTS = ("stays_in_weekend_nights", "stays_in_week_nights")


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def load_bookings(path: Path) -> pd.DataFrame:
    if not path.exists():
        raise FileNotFoundError(f"Input file does not exist: {path}")
    df = pd.read_csv(path)
    if "arrival_date" not in df.columns:
        missing = [c for c in DATE_PARTS if c not in df.columns]
        if missing:
            raise ValueError(f"Input needs arrival_date or all date parts; missing: {missing}")
        df["arrival_date"] = pd.to_datetime(
            df["arrival_date_year"].astype(str)
            + "-" + df["arrival_date_month"].astype(str)
            + "-" + df["arrival_date_day_of_month"].astype(str),
            format="%Y-%B-%d",
            errors="coerce",
        )
    else:
        df["arrival_date"] = pd.to_datetime(df["arrival_date"], errors="coerce")

    if df["arrival_date"].isna().any():
        bad = int(df["arrival_date"].isna().sum())
        raise ValueError(f"{bad} rows have invalid arrival_date values")

    if "nights" not in df.columns and all(c in df.columns for c in NIGHT_PARTS):
        df["nights"] = df[NIGHT_PARTS[0]] + df[NIGHT_PARTS[1]]

    required = ["hotel", "arrival_date", *FEATURE_COLUMNS]
    missing = sorted(set(required) - set(df.columns))
    if missing:
        raise ValueError(f"Input is missing required prediction columns: {missing}")

    unexpected_hotels = sorted(set(df["hotel"].dropna().astype(str)) - set(EXPECTED_HOTELS))
    if unexpected_hotels:
        raise ValueError(f"Unexpected hotel values: {unexpected_hotels}")
    if df["hotel"].isna().any():
        raise ValueError("hotel contains missing values")
    if df.empty:
        raise ValueError("Input contains zero booking rows")

    return df


def one_sided_lower_quantile(residuals: Iterable[float], alpha: float = 0.01) -> tuple[float, int]:
    """Match the saved conformal run's lower-tail finite-sample rank."""
    values = np.sort(np.asarray(list(residuals), dtype=float))
    if values.size == 0 or not np.isfinite(values).all():
        raise ValueError("Conformal residual state is empty or non-finite")
    rank = int(math.ceil((values.size + 1) * alpha))
    if rank < 1:
        return float("-inf"), rank
    if rank > values.size:
        return float("-inf"), rank
    return float(values[rank - 1]), rank


def validate_model_schema(model) -> None:
    if not hasattr(model, "named_steps") or not {"prep", "model"}.issubset(model.named_steps):
        raise TypeError("Expected a fitted sklearn Pipeline with 'prep' and 'model' steps")
    prep = model.named_steps["prep"]
    transformers = {name: cols for name, _, cols in prep.transformers}
    # Compare with the approved schema in features.py, not a separate hard-coded copy of it.
    expected_cat, expected_num = list(CATEGORICAL), list(NUMERIC)
    found_cat, found_num = list(transformers.get("cat", [])), list(transformers.get("num", []))
    if found_cat != expected_cat or found_num != expected_num:
        raise ValueError(
            "Saved model feature schema does not match the approved features.py schema. "
            f"Model: categorical={found_cat}, numeric={found_num}. "
            f"Approved: categorical={expected_cat}, numeric={expected_num}. "
            "Retrain the artifact on the approved features; do not edit the schema to fit the artifact."
        )


def build_report(
    bookings: pd.DataFrame,
    probabilities: np.ndarray,
    *,
    start: pd.Timestamp,
    nights: int,
    model_name: str,
    q95_lower: float,
    q95_upper: float,
    q99_lower_residual: float,
) -> pd.DataFrame:
    if len(probabilities) != len(bookings):
        raise ValueError("Model returned a different number of probabilities than input rows")
    p = np.asarray(probabilities, dtype=float)
    if not np.isfinite(p).all() or ((p < 0) | (p > 1)).any():
        raise ValueError("Model probabilities must be finite and within [0, 1]")

    work = bookings[["hotel", "arrival_date"]].copy()
    work["_p"] = p
    work["_var"] = p * (1.0 - p)
    agg = work.groupby(["hotel", "arrival_date"], observed=True).agg(
        bookings=("_p", "size"),
        expected_cancellations=("_p", "sum"),
        probability_spread=("_var", lambda x: float(np.sqrt(x.sum()))),
    ).reset_index()

    dates = pd.date_range(start=start, periods=nights, freq="D")
    grid = pd.MultiIndex.from_product(
        [EXPECTED_HOTELS, dates], names=["hotel", "arrival_date"]
    ).to_frame(index=False)
    out = grid.merge(agg, on=["hotel", "arrival_date"], how="left")
    out["bookings"] = out["bookings"].fillna(0).astype(int)

    has_data = out["bookings"] > 0
    out["expected_cancellations"] = out["expected_cancellations"].where(has_data)
    out["probability_spread"] = out["probability_spread"].where(has_data)
    out["interval_95_lower"] = np.where(
        has_data, np.maximum(0.0, out["expected_cancellations"] + q95_lower), np.nan
    )
    out["interval_95_upper"] = np.where(
        has_data,
        np.minimum(out["bookings"], out["expected_cancellations"] + q95_upper),
        np.nan,
    )
    lower99 = np.where(
        has_data, np.maximum(0.0, out["expected_cancellations"] + q99_lower_residual), np.nan
    )
    out["lower_99_policy_bound"] = lower99
    out["recommended_oversell"] = np.where(has_data, np.floor(lower99), np.nan)
    out["recommended_oversell"] = out["recommended_oversell"].astype("Int64")
    out["status"] = np.where(has_data, "OK", "NO_BOOKINGS_DATA")
    out["model"] = model_name

    ordered = [
        "hotel", "arrival_date", "bookings", "expected_cancellations",
        "probability_spread", "interval_95_lower", "interval_95_upper",
        "lower_99_policy_bound", "recommended_oversell", "model", "status",
    ]
    return out[ordered]


def run(args: argparse.Namespace) -> tuple[pd.DataFrame, dict]:
    input_path = Path(args.input).resolve()
    model_path = Path(args.model).resolve()
    state_path = Path(args.conformal_state).resolve()
    quantiles_path = Path(args.quantiles).resolve()
    output_path = Path(args.output).resolve()
    start = pd.Timestamp(args.from_date)

    if args.nights < 1 or args.nights > 90:
        raise ValueError("--nights must be between 1 and 90")

    for path in [model_path, state_path, quantiles_path]:
        if not path.exists():
            raise FileNotFoundError(f"Required frozen artifact not found: {path}")

    bookings = load_bookings(input_path)
    model = joblib.load(model_path)
    validate_model_schema(model)

    state = joblib.load(state_path)
    if state.get("model_name") != "XGBoost":
        raise ValueError(f"Conformal state is for {state.get('model_name')}, not XGBoost")
    q99, q99_rank = one_sided_lower_quantile(state["calibration_signed_residuals"])

    quantiles = json.loads(quantiles_path.read_text(encoding="utf-8"))
    xgb_q = quantiles.get("XGBoost", {})
    if "0.95" not in xgb_q:
        raise ValueError("XGBoost 95% conformal quantiles are missing")
    q95_lower = float(xgb_q["0.95"]["q_lower"])
    q95_upper = float(xgb_q["0.95"]["q_upper"])
    if not np.isfinite([q95_lower, q95_upper, q99]).all() or q95_lower > q95_upper:
        raise ValueError("Invalid conformal quantiles")

    # Only approved prediction features are passed to the model.
    X = make_features(bookings)
    probabilities = model.predict_proba(X)[:, 1]

    report = build_report(
        bookings, probabilities, start=start, nights=args.nights,
        model_name="XGBoost", q95_lower=q95_lower, q95_upper=q95_upper,
        q99_lower_residual=q99,
    )

    output_path.parent.mkdir(parents=True, exist_ok=True)
    report.to_csv(output_path, index=False)

    run_id = str(uuid.uuid4())
    manifest = {
        "run_id": run_id,
        "status": "SUCCESS_WITH_MISSING_NIGHT_FLAGS" if (report["status"] != "OK").any() else "SUCCESS",
        "run_timestamp_utc": pd.Timestamp.now(tz="UTC").isoformat(),
        "input_path": str(input_path),
        "input_sha256": sha256(input_path),
        "input_rows": int(len(bookings)),
        "rows_scored": int(len(probabilities)),
        "requested_from": start.date().isoformat(),
        "requested_nights": int(args.nights),
        "report_rows": int(len(report)),
        "missing_hotel_nights": int((report["status"] != "OK").sum()),
        "model_name": "XGBoost",
        "model_path": str(model_path),
        "model_sha256": sha256(model_path),
        "conformal_state_path": str(state_path),
        "conformal_state_sha256": sha256(state_path),
        "quantiles_path": str(quantiles_path),
        "quantiles_sha256": sha256(quantiles_path),
        "conformal_calibration_nights": int(len(state["calibration_signed_residuals"])),
        "one_sided_99_lower_residual_quantile": q99,
        "one_sided_99_lower_rank": q99_rank,
        "two_sided_95_q_lower": q95_lower,
        "two_sided_95_q_upper": q95_upper,
        "policy": "floor(max(0, expected_cancellations + one_sided_99pct_lower_residual_quantile))",
        "feature_columns": list(FEATURE_COLUMNS),
        "forbidden_target_and_post_outcome_fields_excluded": True,
        "code_python": platform.python_version(),
        "code_pandas": pd.__version__,
        "code_sklearn": sklearn.__version__,
        "code_xgboost": xgboost.__version__,
        "output_path": str(output_path),
        "output_sha256": sha256(output_path),
        "limitations": [
            "Booking-time availability of source features is not verified.",
            "Booking rows are not verified physical rooms or individual guests.",
            "Conformal coverage may be affected by temporal dependence and distribution shift.",
            "No physical room capacity or actual walk records are available.",
        ],
    }
    manifest_path = output_path.with_suffix(".manifest.json")
    manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    return report, manifest


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate frozen-model 14-night overbooking recommendations.")
    parser.add_argument("--input", default="data/hotels.csv", help="Booking extract CSV")
    parser.add_argument("--from", dest="from_date", required=True, help="First arrival date, YYYY-MM-DD")
    parser.add_argument("--nights", type=int, default=14, help="Number of consecutive arrival nights")
    parser.add_argument("--model", default="models/xgboost.joblib", help="Frozen XGBoost model artifact")
    parser.add_argument("--conformal-state", default="models/xgboost_conformal_state.joblib")
    parser.add_argument("--quantiles", default="models/conformal_quantiles.json")
    parser.add_argument("--output", default="outputs/nightly_recommendations.csv")
    return parser.parse_args()


if __name__ == "__main__":
    report, manifest = run(parse_args())
    print(report.to_string(index=False))
    print(f"\nRun status: {manifest['status']}")
    print(f"Manifest: {Path(manifest['output_path']).with_suffix('.manifest.json')}")
