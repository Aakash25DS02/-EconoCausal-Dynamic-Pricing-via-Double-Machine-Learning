import unittest
import math
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


class TestEconoCausalAPI(unittest.TestCase):

    def test_health_endpoint(self):
        """Check that the API is running correctly."""
        response = client.get("/health")

        self.assertEqual(response.status_code, 200)

        data = response.json()
        self.assertEqual(data["status"], "ok")

    def test_data_summary_endpoint(self):
        """Check that the dataset summary contains valid information."""
        response = client.get("/data/summary")

        self.assertEqual(response.status_code, 200)

        data = response.json()

        self.assertEqual(data["rows"], 2000)
        self.assertIn("purchase_rate", data)
        self.assertIn("average_discount", data)

        self.assertGreaterEqual(data["purchase_rate"], 0)
        self.assertLessEqual(data["purchase_rate"], 1)

        self.assertGreaterEqual(data["average_discount"], 0)
        self.assertLessEqual(data["average_discount"], 0.35)

    def test_data_preview_endpoint(self):
        """Check that the data preview returns records."""
        response = client.get("/data/preview")

        self.assertEqual(response.status_code, 200)

        data = response.json()

        self.assertTrue(len(data) > 0)

    def test_discount_recommendation_endpoint(self):
        """Check that the discount recommendation is valid."""
        response = client.get("/discount/recommendation")

        self.assertEqual(response.status_code, 200)

        data = response.json()

        # Check the dataset and number of evaluated scenarios.
        self.assertEqual(data["observations"], 2000)
        self.assertEqual(data["scenarios_evaluated"], 36)

        # Check that the recommended discount is between 0 and 0.35.
        discount = data["recommended_discount"]

        self.assertGreaterEqual(discount, 0)
        self.assertLessEqual(discount, 0.35)

        # Discounts should increase in steps of 0.01.
        self.assertAlmostEqual(
            discount * 100,
            round(discount * 100),
            places=7,
        )

        # Check that the predicted purchase probability is valid.
        probability = data["predicted_purchase_probability"]

        self.assertGreaterEqual(probability, 0)
        self.assertLessEqual(probability, 1)
        self.assertTrue(math.isfinite(probability))

        # Check the estimated revenue value.
        revenue = data["estimated_revenue_per_record"]

        self.assertGreaterEqual(revenue, 0)
        self.assertTrue(math.isfinite(revenue))

        # Check all 36 discount scenarios.
        scenarios = data["all_scenarios"]

        self.assertEqual(len(scenarios), 36)

        self.assertAlmostEqual(scenarios[0]["discount"], 0.0)
        self.assertAlmostEqual(scenarios[-1]["discount"], 0.35)

        # Verify every scenario has valid values.
        for scenario in scenarios:
            scenario_discount = scenario["discount"]
            scenario_probability = scenario[
                "predicted_purchase_probability"
            ]
            scenario_revenue = scenario[
                "estimated_revenue_per_record"
            ]

            self.assertGreaterEqual(scenario_discount, 0)
            self.assertLessEqual(scenario_discount, 0.35)

            self.assertTrue(math.isfinite(scenario_discount))
            self.assertTrue(math.isfinite(scenario_probability))
            self.assertTrue(math.isfinite(scenario_revenue))

            self.assertGreaterEqual(scenario_probability, 0)
            self.assertLessEqual(scenario_probability, 1)

            self.assertGreaterEqual(scenario_revenue, 0)

    def test_unknown_endpoint_returns_404(self):
        """Check that an unknown API endpoint returns 404."""
        response = client.get("/this-endpoint-does-not-exist")

        self.assertEqual(response.status_code, 404)


if __name__ == "__main__":
    unittest.main(verbosity=2)