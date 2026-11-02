import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))

from causal_service import CausalPricingService


@pytest.fixture(scope="module")
def trained_service():
    rng = np.random.default_rng(42)
    n = 600

    discount = rng.uniform(0, 0.35, n)
    price = rng.normal(100, 12, n).clip(40, 180)
    promotion = rng.integers(0, 2, n)
    season = rng.choice(["low", "medium", "high"], n)

    competitor_price = rng.normal(98, 10, n).clip(40, 180)

    season_effect = pd.Series(season).map({
        "low": -0.2,
        "medium": 0.0,
        "high": 0.2,
    }).to_numpy()

    logit = (
        -2.0
        + 4.0 * discount
        - 0.012 * (price - 100)
        + 0.25 * promotion
        + season_effect
    )

    probability = 1 / (1 + np.exp(-logit))
    purchase = rng.binomial(1, probability)

    data = pd.DataFrame({
        "customer_id": np.arange(1, n + 1),
        "price": price,
        "discount": discount,
        "competitor_price": competitor_price,
        "promotion": promotion,
        "season": season,
        "purchase": purchase,
    })

    service = CausalPricingService()
    service.fit(data)

    return data, service


def test_model_training(trained_service):
    data, service = trained_service

    assert service.model is not None
    assert service.training_summary["rows_used"] == len(data)
    assert service.training_summary["unique_customers"] == len(data)


def test_estimates_preserve_customer_ids(trained_service):
    data, service = trained_service
    customers = data.head(50)

    results = service.estimate_ite(
        customers,
        reference_discount=0.0,
        target_discount=0.10,
    )

    assert len(results) == 50
    assert results["customer_id"].tolist() == (
        customers["customer_id"].tolist()
    )


def test_estimates_are_finite(trained_service):
    data, service = trained_service

    results = service.estimate_ite(data.head(50))

    assert np.isfinite(results["estimated_effect"]).all()


def test_invalid_discount_is_rejected(trained_service):
    data, service = trained_service

    with pytest.raises(ValueError, match="Target discount"):
        service.estimate_ite(
            data.head(10),
            reference_discount=0.0,
            target_discount=0.50,
        )


def test_duplicate_customer_ids_are_rejected(trained_service):
    data, _ = trained_service
    duplicate_data = data.copy()
    duplicate_data.loc[1, "customer_id"] = (
        duplicate_data.loc[0, "customer_id"]
    )

    service = CausalPricingService()

    with pytest.raises(ValueError, match="unique"):
        service.fit(duplicate_data)


def test_effect_summary(trained_service):
    data, service = trained_service
    results = service.estimate_ite(data.head(40))

    summary = service.summarize(results)

    assert summary["customer_count"] == 40
    assert "mean_effect" in summary
    assert "positive_effect_customers" in summary
    assert "negative_effect_customers" in summary


def test_untrained_service_is_rejected(trained_service):
    data, _ = trained_service
    service = CausalPricingService()

    with pytest.raises(RuntimeError, match="fit"):
        service.estimate_ite(data.head(10))
