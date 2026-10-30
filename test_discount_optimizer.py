import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
import numpy as np
import pandas as pd
from discount_optimizer import recommend_discount

class TestDiscountOptimizer(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.path = Path(self.temp.name) / "pricing_data.csv"
        self.df = pd.DataFrame({"price": [100 + i for i in range(40)], "discount": [0.1] * 40, "competitor_price": [110 + i for i in range(40)], "promotion": [i % 2 for i in range(40)], "season": ["high" if i % 2 else "low" for i in range(40)], "purchase": [i % 2 for i in range(40)]})
        self.df.to_csv(self.path, index=False)
        self.patcher = patch("discount_optimizer.DATA_PATH", self.path)
        self.patcher.start()

    def tearDown(self):
        self.patcher.stop()
        self.temp.cleanup()

    def test_recommendation_returns_valid_results(self):
        result = recommend_discount()
        self.assertEqual(result["observations"], 40)
        self.assertEqual(result["scenarios_evaluated"], 36)
        self.assertEqual(len(result["all_scenarios"]), 36)
        self.assertTrue(0 <= result["recommended_discount"] <= 0.35)
        self.assertTrue(np.isfinite(result["estimated_revenue_per_record"]))

    def test_missing_required_columns_raises_value_error(self):
        self.df.drop(columns=["purchase"]).to_csv(self.path, index=False)
        with self.assertRaises(ValueError):
            recommend_discount()

    def test_empty_dataset_raises_value_error(self):
        pd.DataFrame(columns=self.df.columns).to_csv(self.path, index=False)
        with self.assertRaises(ValueError):
            recommend_discount()

    def test_missing_values_raise_value_error(self):
        self.df.loc[0, "discount"] = np.nan
        self.df.to_csv(self.path, index=False)
        with self.assertRaises(ValueError):
            recommend_discount()

    def test_invalid_purchase_values_raise_value_error(self):
        self.df["purchase"] = [2 if i == 0 else i % 2 for i in range(40)]
        self.df.to_csv(self.path, index=False)
        with self.assertRaises(ValueError):
            recommend_discount()

    def test_missing_dataset_raises_file_not_found_error(self):
        self.path.unlink()
        with self.assertRaises(FileNotFoundError):
            recommend_discount()

if __name__ == "__main__":
    unittest.main(verbosity=2)
