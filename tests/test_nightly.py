import sys
import unittest
from pathlib import Path
import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from nightly import build_report, one_sided_lower_quantile


class NightlyTests(unittest.TestCase):
    def test_one_sided_quantile_matches_rank_rule(self):
        q, rank = one_sided_lower_quantile(range(148), alpha=0.01)
        self.assertEqual(rank, 2)
        self.assertEqual(q, 1.0)

    def test_build_report_aggregates_and_flags_missing(self):
        bookings = pd.DataFrame({
            "hotel": ["City Hotel", "City Hotel"],
            "arrival_date": pd.to_datetime(["2017-08-18", "2017-08-18"]),
        })
        report = build_report(
            bookings, np.array([0.2, 0.3]), start=pd.Timestamp("2017-08-18"),
            nights=2, model_name="XGBoost", q95_lower=-2, q95_upper=4,
            q99_lower_residual=-3,
        )
        city = report[(report.hotel == "City Hotel") & (report.arrival_date == pd.Timestamp("2017-08-18"))].iloc[0]
        self.assertEqual(city.bookings, 2)
        self.assertAlmostEqual(city.expected_cancellations, 0.5)
        self.assertEqual(int(city.recommended_oversell), 0)
        missing = report[(report.hotel == "Resort Hotel") & (report.arrival_date == pd.Timestamp("2017-08-19"))].iloc[0]
        self.assertEqual(missing.status, "NO_BOOKINGS_DATA")
        self.assertTrue(pd.isna(missing.recommended_oversell))


if __name__ == "__main__":
    unittest.main()
