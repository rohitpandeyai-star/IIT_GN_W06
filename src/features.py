"""Conservative candidate feature extraction for the hotel cancellation project.

This module deliberately uses only the candidate first-bin columns from docs/COLUMNS.md.
It does not perform model fitting, target encoding, or imputation of children.
The source CSV is a near-arrival snapshot rather than a guaranteed original-booking snapshot;
validate the fields against the PMS change log before production use.
"""
from __future__ import annotations

import pandas as pd

TARGET = "is_canceled"

# Approved candidate fields (notebooks/pipeline/05_feature_engineering.ipynb, docs/DECISIONS.md P3).
# Revisit after verifying original-booking timestamps.
CATEGORICAL = (
    "hotel",
    "market_segment",
    "distribution_channel",
    "agent",
    "company",
)
NUMERIC = (
    "is_repeated_guest",
    "previous_cancellations",
    "previous_bookings_not_canceled",
)
FEATURE_COLUMNS = CATEGORICAL + NUMERIC

# Held back until booking-time availability is proven: the source paper warns that the correct
# nationality is often known only at check-in, so `country` can differ because of the outcome.
HELD_BACK = {"country"}

FORBIDDEN = {
    "is_canceled",
    "reservation_status",
    "reservation_status_date",
    "booking_changes",
    "assigned_room_type",
}


def make_features(bookings: pd.DataFrame) -> pd.DataFrame:
    """Return candidate first-bin features in the original row order.

    Missing `agent` and `company` are meaningful no-partner categories per docs/DOMAIN.md.
    Other candidate numeric fields are required and are not silently imputed.
    """
    missing = [c for c in FEATURE_COLUMNS if c not in bookings.columns]
    if missing:
        raise ValueError(f"Missing required feature columns: {missing}")

    X = bookings.loc[:, FEATURE_COLUMNS].copy()

    for col in ("agent", "company"):
        X[col] = X[col].astype("string").fillna("NO_" + col.upper())

    for col in ("hotel", "market_segment", "distribution_channel"):
        X[col] = X[col].astype("string").fillna("UNKNOWN_" + col.upper())

    for col in NUMERIC:
        if X[col].isna().any():
            raise ValueError(f"Unexpected missing values in candidate numeric feature {col}")

    # IDs and labels remain categorical strings; do not treat them as ordered magnitudes.
    return X


def make_target(bookings: pd.DataFrame) -> pd.Series:
    """Return the contract target, after validating its binary domain."""
    if TARGET not in bookings.columns:
        raise ValueError(f"Missing target column: {TARGET}")
    y = bookings[TARGET].astype("int8")
    if not y.isin([0, 1]).all():
        raise ValueError("is_canceled must contain only 0 and 1")
    return y
