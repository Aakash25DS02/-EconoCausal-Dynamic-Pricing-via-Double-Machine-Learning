import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))

from data_drift_detector import detect_data_drift


@pytest.fixture
def reference_data():
    rng = np.random.default_rng(42)
    n = 600

    return pd.DataFrame({
        "customer_id": np.arange(n),
        "price": rng.normal(100, 12, n).clip(40, 180),
        "discount": rng.uniform(0, 0.35, n),
        "competitor_price": rng.normal(98, 10, n).clip(40, 180),
        "promotion": rng.integers(0, 2, n),
        "season": rng.choice(["low", "medium", "high"], n),
        "purchase": rng.integers(0, 2, n),
    })


def test_identical_data_is_stable(reference_data):
    report = detect_data_drift(reference_data, reference_data.copy())

    assert report["status"] == "NO_SIGNIFICANT_DRIFT"
    assert report["drifted_features"] == []


def test_shifted_data_is_flagged(reference_data):
    current = reference_data.copy()
    current["price"] *= 1.5
    current["discount"] = np.clip(
        current["discount"] + 0.18, 0, 0.35
    )
    current["purchase"] = 1

    report = detect_data_drift(reference_data, current)

    assert report["status"] == "DRIFT_DETECTED"
    assert "price" in report["drifted_features"]
    assert "purchase" in report["drifted_features"]


def test_missing_column_is_rejected(reference_data):
    current = reference_data.drop(columns=["discount"])

    with pytest.raises(ValueError, match="missing columns"):
        detect_data_drift(reference_data, current)


def test_missing_values_are_rejected(reference_data):
    current = reference_data.copy()
    current.loc[0, "price"] = np.nan

    with pytest.raises(ValueError, match="missing monitored values"):
        detect_data_drift(reference_data, current)


def test_invalid_threshold_is_rejected(reference_data):
    with pytest.raises(ValueError, match="PSI threshold"):
        detect_data_drift(
            reference_data,
            reference_data,
            psi_threshold=0
        )
