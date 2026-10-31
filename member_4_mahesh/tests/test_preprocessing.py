
import pandas as pd
import pytest

from member_4_mahesh.data_processing.data_validator import validate_dataset
from member_4_mahesh.data_processing.preprocessing import (
    MODEL_FEATURES,
    get_model_data,
    preprocess_data,
)


@pytest.fixture
def sample_data():
    return pd.DataFrame({
        "customer_id": ["C001", "C002", "C003"],
        "age": [25, 35, 45],
        "tenure_months": [6, 12, 24],
        "past_purchases": [3, 8, 12],
        "avg_order_value": [500.0, 700.0, 900.0],
        "days_since_last_purchase": [10, 20, 5],
        "website_visits_30d": [5, 8, 12],
        "cart_abandonment_rate": [0.2, 0.4, 0.1],
        "support_tickets_90d": [0, 1, 2],
        "price_sensitivity": [0.3, 0.6, 0.8],
        "treatment": [0, 1, 0],
        "discount_amount": [0.0, 100.0, 0.0],
        "churned": [1, 0, 1],
        "purchased_again": [0, 1, 0],
        "revenue": [0.0, 800.0, 0.0],
        "profit": [0.0, 200.0, 0.0],
    })


def test_valid_dataset(sample_data):
    report = validate_dataset(sample_data)
    assert report["valid"] is True
    assert report["rows"] == 3