
import unittest

from dml_model import estimate_discount_effect


class TestDMLModel(unittest.TestCase):

    def test_estimate_returns_valid_results(self):
        result = estimate_discount_effect()

        self.assertEqual(result["observations"], 2000)
        self.assertEqual(result["treatment"], "discount")
        self.assertEqual(result["outcome"], "purchase")
        self.assertEqual(result["validation"], "passed")

        self.assertTrue(
            isinstance(
                result["estimated_effect_per_1_0_discount"],
                float,
            )
        )

        self.assertTrue(
            -1.0 < result["estimated_effect_per_1_0_discount"] < 1.0
        )

        self.assertAlmostEqual(
            result["estimated_effect_per_0_01_discount"],
            result["estimated_effect_per_1_0_discount"] * 0.01,
            places=10,
        )


if __name__ == "__main__":
    unittest.main()
