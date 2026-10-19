
import pandas as pd
import pytest

from member_4_mahesh.data_processing.preprocessing import (
    MODEL_FEATURES,
    get_model_data,
    preprocess_data,
)


@pytest.fixture
def sample_data():
    return pd.DataFrame({
        "customer_id": ["C001", "C002", "C003", "C004"],
        "age": [25, 32, 41, 28],
        "tenure_months": [12, 24, 36, 8],
        "past_purchases": [5, 10, 15, 3],
        "avg_order_value": [50.0, 80.0, 100.0, 40.0],
        "days_since_last_purchase": [10, 30, 45, 5],
        "website_visits_30d": [12, 8, 5, 20],
        "cart_abandonment_rate": [0.2, 0.5, 0.6, 0.1],
        "support_tickets_90d": [0, 1, 2, 0],
        "price_sensitivity": [0.4, 0.7, 0.8, 0.3],
        "treatment": [0, 1, 0, 1],
        "discount_amount": [0, 10, 0, 5],
        "churned": [1, 0, 1, 0],
        "purchased_again": [0, 1, 0, 1],
        "revenue": [100, 200, 120, 80],
        "profit": [20, 40, 25, 15],
    })


def test_preprocessing_preserves_rows(sample_data):
    processed = preprocess_data(sample_data)
    assert len(processed) == len(sample_data)


def test_model_data_shapes(sample_data):
    X, T, Y = get_model_data(sample_data)

    assert list(X.columns) == MODEL_FEATURES
    assert X.shape == (4, len(MODEL_FEATURES))
    assert len(T) == 4
    assert len(Y) == 4


def test_no_treatment_or_outcome_leakage(sample_data):
    X, _, _ = get_model_data(sample_data)

    assert "treatment" not in X.columns
    assert "discount_amount" not in X.columns
    assert "churned" not in X.columns
    assert "purchased_again" not in X.columns
    assert "profit" not in X.columns


def test_invalid_rate_fails(sample_data):
    sample_data.loc[0, "price_sensitivity"] = 1.5

    with pytest.raises(ValueError, match="price_sensitivity"):
        preprocess_data(sample_data)