"""Nightly overbooking recommendations from the frozen choice (models/frozen_choice.json).

Example:
    python src/nightly.py --from 2017-08-18 --nights 14

For each hotel and arrival night it prints two oversell counts, both with the rule
k = max(0, floor(expected cancellations) - buffer):
  - the flat rule (each hotel's Train cancellation rate, buffers City 20 / Resort 4): the policy the
    deck recommends;
  - the frozen CatBoost model (buffers City 6 / Resort 3), shown alongside: on the 2017 test it cost
    EUR 150,459 more than the flat rule (notebooks/14_test_run.ipynb).

Inference only: it never fits, tunes or recalibrates anything, and it refuses to run if the model or
preprocessor file differs from the fingerprint recorded at the freeze. It never reads `is_canceled`.
The input is the final-book export, not a snapshot of the reservations on the books on a real
morning, so this is a historical replay, not a live forecast.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import platform
import sys
import uuid
import warnings
from pathlib import Path

import joblib
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(Path(__file__).resolve().parent))
from features import FEATURE_COLUMNS, FORBIDDEN  # noqa: E402

EXPECTED_HOTELS = ("City Hotel", "Resort Hotel")
DATE_PARTS = ("arrival_date_year", "arrival_date_month", "arrival_date_day_of_month")


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def load_freeze(path: Path) -> dict:
    """Read the frozen choice and refuse to go on if a frozen file has changed since the freeze."""
    freeze = json.loads(path.read_text(encoding="utf-8"))
    for key in ("model", "preprocessor"):
        file = ROOT / freeze[f"{key}_file"]
        if not file.exists():
            raise FileNotFoundError(f"Frozen {key} file not found: {file}")
        if sha256(file) != freeze[f"{key}_sha256"]:
            raise ValueError(f"{file} differs from the fingerprint recorded at the freeze; refusing to run.")
    return freeze


def load_bookings(path: Path, start: pd.Timestamp, nights: int) -> pd.DataFrame:
    """Bookings due to arrive in the requested nights, with the 8 inputs labelled as in notebook 05."""
    if not path.exists():
        raise FileNotFoundError(f"Input file does not exist: {path}")
    df = pd.read_csv(path, dtype={"agent": str, "company": str}, low_memory=False)
    if "arrival_date" in df.columns:
        df["arrival_date"] = pd.to_datetime(df["arrival_date"], errors="coerce")
    else:
        missing = [c for c in DATE_PARTS if c not in df.columns]
        if missing:
            raise ValueError(f"Input needs arrival_date or all date parts; missing: {missing}")
        df["arrival_date"] = pd.to_datetime(
            df["arrival_date_year"].astype(str) + "-" + df["arrival_date_month"].astype(str)
            + "-" + df["arrival_date_day_of_month"].astype(str), format="%Y-%B-%d", errors="coerce")
    if df["arrival_date"].isna().any():
        raise ValueError(f"{int(df['arrival_date'].isna().sum())} rows have invalid arrival dates")

    missing = sorted(set(FEATURE_COLUMNS) - set(df.columns))
    if missing:
        raise ValueError(f"Input is missing required prediction columns: {missing}")
    unexpected = sorted(set(df["hotel"].dropna().astype(str)) - set(EXPECTED_HOTELS))
    if unexpected or df["hotel"].isna().any():
        raise ValueError(f"Unexpected or missing hotel values: {unexpected}")

    end = start + pd.Timedelta(days=nights)
    window = df[(df["arrival_date"] >= start) & (df["arrival_date"] < end)].copy()
    # Cleaning choice C2 (notebook 05): agent and company are labels; a blank ('NULL') means none.
    for col in ("agent", "company"):
        window[col] = window[col].fillna("none").astype(str)
    for col in FEATURE_COLUMNS:
        if window[col].isna().any():
            raise ValueError(f"Unexpected missing values in input {col}")
    return window


def oversell(expected: pd.Series, buffers: dict) -> pd.Series:
    """k = max(0, floor(expected) - buffer), with the buffer for each row's hotel."""
    b = expected.index.get_level_values("hotel").map(buffers).to_numpy(dtype=float)
    return pd.Series(np.maximum(np.floor(expected.to_numpy()) - b, 0), index=expected.index)


def build_report(bookings: pd.DataFrame, p_flat: np.ndarray, p_model: np.ndarray, *, start: pd.Timestamp,
                 nights: int, flat_buffers: dict, model_buffers: dict) -> pd.DataFrame:
    """One row per hotel and night: bookings on the books, expected cancellations and oversell per method."""
    for p in (p_flat, p_model):
        p = np.asarray(p, dtype=float)
        if len(p) != len(bookings) or not np.isfinite(p).all() or ((p < 0) | (p > 1)).any():
            raise ValueError("Each method needs one probability in [0, 1] per booking")
    work = bookings[["hotel", "arrival_date"]].assign(_flat=p_flat, _model=p_model)
    agg = work.groupby(["hotel", "arrival_date"]).agg(
        bookings=("_flat", "size"), flat_expected=("_flat", "sum"), model_expected=("_model", "sum"))
    grid = pd.MultiIndex.from_product([EXPECTED_HOTELS, pd.date_range(start, periods=nights, freq="D")],
                                      names=["hotel", "arrival_date"])
    out = agg.reindex(grid)
    has_data = out["bookings"].notna()
    out["bookings"] = out["bookings"].fillna(0).astype(int)
    out["flat_oversell"] = oversell(out["flat_expected"].fillna(0), flat_buffers).where(has_data).astype("Int64")
    out["model_oversell"] = oversell(out["model_expected"].fillna(0), model_buffers).where(has_data).astype("Int64")
    out["status"] = np.where(has_data, "OK", "NO_BOOKINGS_DATA")
    out = out.reset_index()
    return out[["hotel", "arrival_date", "bookings", "flat_expected", "flat_oversell",
                "model_expected", "model_oversell", "status"]]


def run(args: argparse.Namespace) -> tuple[pd.DataFrame, dict]:
    if not 1 <= args.nights <= 90:
        raise ValueError("--nights must be between 1 and 90")
    start = pd.Timestamp(args.from_date)
    freeze_path, input_path, output_path = (Path(args.freeze).resolve(), Path(args.input).resolve(),
                                            Path(args.output).resolve())
    freeze = load_freeze(freeze_path)
    preprocessor = joblib.load(ROOT / freeze["preprocessor_file"])
    model = joblib.load(ROOT / freeze["model_file"])
    if set(preprocessor.feature_names_in_) != set(FEATURE_COLUMNS):
        raise ValueError(f"Frozen preprocessor inputs {list(preprocessor.feature_names_in_)} differ from "
                         f"the approved features.py inputs {list(FEATURE_COLUMNS)}")

    bookings = load_bookings(input_path, start, args.nights)
    X = bookings[list(preprocessor.feature_names_in_)]
    assert not FORBIDDEN & set(X.columns), "an outcome column reached the model"
    with warnings.catch_warnings():
        # Agents/companies never seen in Train go to the 'infrequent' column by design (notebook 10).
        warnings.filterwarnings("ignore", message="Found unknown categories", category=UserWarning)
        p_model = model.predict_proba(preprocessor.transform(X).to_numpy(dtype=float))[:, 1] if len(X) else np.array([])
    p_flat = bookings["hotel"].map(freeze["flat_rule_hotel_rates_from_train"]).to_numpy(dtype=float)

    buffers = freeze["primary"]
    report = build_report(bookings, p_flat, p_model, start=start, nights=args.nights,
                          flat_buffers=buffers["flat_rule_buffers"], model_buffers=buffers["chosen_buffers"])
    output_path.parent.mkdir(parents=True, exist_ok=True)
    report.to_csv(output_path, index=False)

    manifest = {
        "run_id": str(uuid.uuid4()),
        "status": "SUCCESS_WITH_MISSING_NIGHT_FLAGS" if (report["status"] != "OK").any() else "SUCCESS",
        "run_timestamp_utc": pd.Timestamp.now(tz="UTC").isoformat(),
        "input_path": str(input_path), "input_sha256": sha256(input_path), "bookings_scored": int(len(bookings)),
        "requested_from": start.date().isoformat(), "requested_nights": int(args.nights),
        "freeze_file": str(freeze_path), "freeze_sha256": sha256(freeze_path), "frozen_at": freeze["frozen_at"],
        "model": freeze["chosen_method"], "model_sha256": freeze["model_sha256"],
        "preprocessor_sha256": freeze["preprocessor_sha256"], "fingerprints_checked": True,
        "rule": freeze["rule"],
        "policy_recommended": {"method": "flat rule", "hotel_rates": freeze["flat_rule_hotel_rates_from_train"],
                               "buffers": buffers["flat_rule_buffers"]},
        "model_shown_alongside": {"method": freeze["chosen_method"], "buffers": buffers["chosen_buffers"]},
        "inputs": list(FEATURE_COLUMNS), "outcome_column_read": False,
        "python": platform.python_version(),
        "output_path": str(output_path), "output_sha256": sha256(output_path),
        "limitations": [
            "Final-book export, not a snapshot of the reservations on the books on a real morning.",
            "Booking-time availability of four provisional inputs is not verified.",
            "Booking rows are not verified rooms; there is no room capacity in the data.",
        ],
    }
    output_path.with_suffix(".manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    return report, manifest


def show(report: pd.DataFrame, manifest: dict) -> str:
    """The table a revenue manager reads: one block per hotel, the recommended column first."""
    pol, alt = manifest["policy_recommended"], manifest["model_shown_alongside"]
    lines = [f"Frozen choice {Path(manifest['freeze_file']).name} ({manifest['frozen_at']}); model and preprocessor "
             f"fingerprints match.",
             "Rule: oversell = max(0, floor(expected cancellations) - buffer). Outcomes are not read.", ""]
    for hotel in EXPECTED_HOTELS:
        part = report[report["hotel"] == hotel]
        lines.append(f"{hotel}: recommended flat rule (rate {pol['hotel_rates'][hotel]:.1%}, buffer "
                     f"{pol['buffers'][hotel]}) | {alt['method']} shown alongside (buffer {alt['buffers'][hotel]})")
        table = pd.DataFrame({
            "arrival": part["arrival_date"].dt.strftime("%a %d %b %Y"),
            "on books": part["bookings"],
            "flat: expected": part["flat_expected"].round(1),
            "OVERSELL (flat)": part["flat_oversell"],
            f"{alt['method']}: expected": part["model_expected"].round(1),
            f"oversell ({alt['method']})": part["model_oversell"],
        })
        lines += [table.to_string(index=False, na_rep="-"), ""]
    lines.append(f"Run status: {manifest['status']} · {manifest['bookings_scored']:,} bookings scored")
    lines.append(f"Saved: {manifest['output_path']} (+ .manifest.json)")
    lines.append("Historical replay on final-book data, not a live forecast.")
    return "\n".join(lines)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Nightly overbooking recommendations from the frozen choice.")
    parser.add_argument("--input", default="data/hotels.csv", help="Booking extract CSV")
    parser.add_argument("--from", dest="from_date", required=True, help="First arrival date, YYYY-MM-DD")
    parser.add_argument("--nights", type=int, default=14, help="Number of consecutive arrival nights (1-90)")
    parser.add_argument("--freeze", default="models/frozen_choice.json", help="Frozen choice written before the test")
    parser.add_argument("--output", default="outputs/nightly_recommendations.csv")
    return parser.parse_args()


if __name__ == "__main__":
    report, manifest = run(parse_args())
    print(show(report, manifest))
