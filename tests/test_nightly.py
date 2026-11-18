import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
import nightly  # noqa: E402
from nightly import build_report, load_freeze  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]


class NightlyTests(unittest.TestCase):
    def test_build_report_applies_floor_minus_buffer_per_hotel_and_flags_missing(self):
        bookings = pd.DataFrame({
            "hotel": ["City Hotel"] * 3 + ["Resort Hotel"],
            "arrival_date": pd.to_datetime(["2017-08-18"] * 4),
        })
        report = build_report(
            bookings, np.array([0.9, 0.9, 0.9, 0.5]), np.array([0.6, 0.6, 0.6, 0.5]),
            start=pd.Timestamp("2017-08-18"), nights=2,
            flat_buffers={"City Hotel": 1, "Resort Hotel": 0}, model_buffers={"City Hotel": 0, "Resort Hotel": 0},
        )
        city = report[(report.hotel == "City Hotel") & (report.arrival_date == pd.Timestamp("2017-08-18"))].iloc[0]
        self.assertEqual(city.bookings, 3)
        self.assertAlmostEqual(city.flat_expected, 2.7)
        self.assertEqual(int(city.flat_oversell), 1)    # floor(2.7) - 1
        self.assertEqual(int(city.model_oversell), 1)   # floor(1.8) - 0
        resort = report[(report.hotel == "Resort Hotel") & (report.arrival_date == pd.Timestamp("2017-08-18"))].iloc[0]
        self.assertEqual(int(resort.flat_oversell), 0)  # never below zero
        missing = report[report.arrival_date == pd.Timestamp("2017-08-19")]
        self.assertTrue((missing.status == "NO_BOOKINGS_DATA").all())
        self.assertTrue(missing.flat_oversell.isna().all())

    @unittest.skipUnless((ROOT / "data" / "hotels.csv").exists() and (ROOT / "data" / "models" / "test_predictions.csv").exists(),
                         "needs data/hotels.csv and notebook 14's saved predictions")
    def test_reproduces_notebook_14_predictions(self):
        with tempfile.TemporaryDirectory() as tmp:
            args = type("Args", (), {"input": str(ROOT / "data" / "hotels.csv"), "from_date": "2017-08-18", "nights": 14,
                                     "freeze": str(ROOT / "models" / "frozen_choice.json"),
                                     "output": str(Path(tmp) / "out.csv")})()
            report, manifest = nightly.run(args)
        test = pd.read_csv(ROOT / "data" / "splits" / "test.csv", index_col="row", parse_dates=["arrival_date"])
        pred = pd.read_csv(ROOT / "data" / "models" / "test_predictions.csv", index_col="row")
        d = test[["hotel", "arrival_date"]].join(pred)
        d = d[(d.arrival_date >= "2017-08-18") & (d.arrival_date <= "2017-08-31")]
        ref = d.groupby(["hotel", "arrival_date"])[["CatBoost", "flat-rule reference"]].sum()
        got = report.set_index(["hotel", "arrival_date"]).loc[ref.index]
        np.testing.assert_allclose(got["model_expected"], ref["CatBoost"], atol=1e-9)
        np.testing.assert_allclose(got["flat_expected"], ref["flat-rule reference"], atol=1e-9)
        self.assertFalse(manifest["outcome_column_read"])

    def test_refuses_a_changed_model_file(self):
        freeze = json.loads((ROOT / "models" / "frozen_choice.json").read_text(encoding="utf-8"))
        with tempfile.TemporaryDirectory() as tmp:
            tmp = Path(tmp)
            for key in ("model", "preprocessor"):
                target = tmp / freeze[f"{key}_file"]
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy(ROOT / freeze[f"{key}_file"], target)
            with open(tmp / freeze["model_file"], "ab") as f:
                f.write(b"tampered")
            (tmp / "freeze.json").write_text(json.dumps(freeze), encoding="utf-8")
            original = nightly.ROOT
            nightly.ROOT = tmp
            try:
                with self.assertRaises(ValueError):
                    load_freeze(tmp / "freeze.json")
            finally:
                nightly.ROOT = original


if __name__ == "__main__":
    unittest.main()
