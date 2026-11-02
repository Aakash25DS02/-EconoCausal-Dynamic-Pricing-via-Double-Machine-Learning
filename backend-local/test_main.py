import unittest

from fastapi.testclient import TestClient

from main import app

client = TestClient(app)


class TestBackendLocalAPI(unittest.TestCase):

    def test_root_endpoint(self):
        response = client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["project"], "EconoCausal")

    def test_health_endpoint(self):
        response = client.get("/health")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["status"], "ok")

    def test_data_summary_endpoint(self):
        response = client.get("/data/summary")
        self.assertEqual(response.status_code, 200)

        data = response.json()
        self.assertEqual(data["rows"], 2000)
        self.assertIn("purchase_rate", data)
        self.assertIn("average_discount", data)
        self.assertEqual(sum(data["missing_values"].values()), 0)

    def test_data_preview_endpoint(self):
        response = client.get("/data/preview")
        self.assertEqual(response.status_code, 200)

        records = response.json()["records"]
        self.assertEqual(len(records), 10)
        self.assertIn("customer_id", records[0])

    def test_promotion_effect_endpoint(self):
        response = client.get("/analysis/promotion-effect")
        self.assertEqual(response.status_code, 200)

        data = response.json()
        self.assertEqual(data["observations"], 2000)
        self.assertIn("adjusted_effect", data)
        self.assertIn("confidence_interval_95", data)
        self.assertIn("causal_warning", data)

    def test_promotion_effect_dml_endpoint(self):
        response = client.get("/analysis/promotion-effect-dml")
        self.assertEqual(response.status_code, 200)

        data = response.json()
        self.assertEqual(data["observations"], 2000)
        self.assertIn("dml_effect", data)
        self.assertIn("confidence_interval_95", data)
        self.assertIn("causal_warning", data)

    def test_budget_allocation_endpoint(self):
        response = client.post(
            "/allocation/optimize",
            json={"budget": 10000}
        )
        self.assertEqual(response.status_code, 200)

        data = response.json()
        self.assertEqual(data["status"], "success")
        self.assertEqual(data["customer_count"], 2000)
        self.assertLessEqual(
            data["expected_discount_spend"], 10000
        )
        self.assertGreaterEqual(data["remaining_budget"], 0)
        self.assertEqual(len(data["allocations"]), 2000)

    def test_zero_budget_returns_422(self):
        response = client.post(
            "/allocation/optimize",
            json={"budget": 0}
        )
        self.assertEqual(response.status_code, 422)

    def test_negative_budget_returns_422(self):
        response = client.post(
            "/allocation/optimize",
            json={"budget": -100}
        )
        self.assertEqual(response.status_code, 422)

    def test_unknown_endpoint_returns_404(self):
        response = client.get("/unknown-endpoint")
        self.assertEqual(response.status_code, 404)


if __name__ == "__main__":
    unittest.main(verbosity=2)