"""The reusable feature code must match the approved feature decision (docs/DECISIONS.md P3).

Run with: pytest -q
"""
import pathlib
import sys

import pandas as pd
import pytest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent / "src"))
import features  # noqa: E402

APPROVED = (
    "hotel", "market_segment", "distribution_channel", "agent", "company",
    "is_repeated_guest", "previous_cancellations", "previous_bookings_not_canceled",
)


def one_booking(**overrides):
    row = {"hotel": "City Hotel", "market_segment": "Online TA", "distribution_channel": "TA/TO",
           "agent": None, "company": None, "is_repeated_guest": 0, "previous_cancellations": 0,
           "previous_bookings_not_canceled": 0, "country": "PRT", "is_canceled": 1}
    row.update(overrides)
    return pd.DataFrame([row])


def test_feature_columns_are_the_approved_set():
    assert features.FEATURE_COLUMNS == APPROVED


def test_held_back_and_post_outcome_fields_are_never_features():
    assert not set(features.FEATURE_COLUMNS) & features.HELD_BACK
    assert not set(features.FEATURE_COLUMNS) & features.FORBIDDEN
    assert "country" in features.HELD_BACK


def test_make_features_drops_country_and_the_target():
    X = features.make_features(one_booking())
    assert tuple(X.columns) == APPROVED
    assert X.loc[0, "agent"] == "NO_AGENT" and X.loc[0, "company"] == "NO_COMPANY"


def test_missing_numeric_feature_is_not_silently_filled():
    with pytest.raises(ValueError):
        features.make_features(one_booking(previous_cancellations=None))
