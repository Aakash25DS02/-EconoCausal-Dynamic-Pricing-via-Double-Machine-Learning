import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
import pandas as pd
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

class TestDatasetValidation(unittest.TestCase):
    def test_missing_required_columns_returns_422(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "invalid.csv"
            pd.DataFrame({"price": [100], "discount": [0.1]}).to_csv(path, index=False)
            with patch("app.main.DATA_PATH", path):
                response = client.get("/data/summary")
        self.assertEqual(response.status_code, 422)

    def test_empty_dataset_returns_422(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "empty.csv"
            pd.DataFrame(columns=["price", "discount", "purchase"]).to_csv(path, index=False)
            with patch("app.main.DATA_PATH", path):
                response = client.get("/data/summary")
        self.assertEqual(response.status_code, 422)

    def test_missing_values_return_422(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "missing.csv"
            pd.DataFrame({"price": [100], "discount": [None], "purchase": [1]}).to_csv(path, index=False)
            with patch("app.main.DATA_PATH", path):
                response = client.get("/data/summary")
        self.assertEqual(response.status_code, 422)

    def test_missing_dataset_returns_404(self):
        with patch("app.main.DATA_PATH", Path("missing_test_dataset.csv")):
            response = client.get("/data/summary")
        self.assertEqual(response.status_code, 404)

if __name__ == "__main__":
    unittest.main(verbosity=2)
