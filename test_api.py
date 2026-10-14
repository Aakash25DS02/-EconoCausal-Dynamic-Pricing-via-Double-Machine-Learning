import unittest
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


class TestEconoCausalAPI(unittest.TestCase):

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

    def test_data_preview_endpoint(self):
        response = client.get("/data/preview")
        self.assertEqual(response.status_code, 200)

        data = response.json()
        self.assertTrue(len(data) > 0)

    def test_discount_recommendation_endpoint(self):
        response = client.get("/discount/recommendation")
        self.assertEqual(response.status_code, 200)

        data = response.json()
        self.assertEqual(data["observations"], 2000)
        self.assertEqual(data["scenarios_evaluated"], 36)
        self.assertGreaterEqual(data["recommended_discount"], 0)
        self.assertLessEqual(data["recommended_discount"], 0.35)
        self.assertIn("estimated_revenue_per_record", data)
        self.assertEqual(len(data["all_scenarios"]), 36)


if __name__ == "__main__":
    unittest.main(verbosity=2)