

import pandas as pd

from .data_loader import load_dataset, save_dataset
from .data_validator import validate_dataset


MODEL_FEATURES = [
    "age",
    "tenure_months",
    "past_purchases",
    "avg_order_value",
    "days_since_last_purchase",
    "website_visits_30d",
    "cart_abandonment_rate",
    "support_tickets_90d",
    "price_sensitivity",
]


def preprocess_data(df: pd.DataFrame) -> pd.DataFrame:
    """Validate and prepare data for causal analysis."""
    validate_dataset(df)

    processed = df.copy()

    # Ensure numeric data has consistent types.
    numeric_columns = [
        col for col in processed.columns
        if col != "customer_id"
    ]

    for col in numeric_columns:
        processed[col] = pd.to_numeric(
            processed[col], errors="raise"
        )

    return processed


def get_model_data(df: pd.DataFrame):
    """Return features X, treatment T, and outcome Y."""
    processed = preprocess_data(df)

    X = processed[MODEL_FEATURES].copy()
    T = processed["treatment"].astype(int)
    Y = processed["churned"].astype(int)

    return X, T, Y


def main():
    df = load_dataset()
    processed = preprocess_data(df)
    output_path = save_dataset(processed)

    X, T, Y = get_model_data(processed)

    print("Preprocessing completed.")
    print(f"Saved dataset: {output_path}")
    print(f"Features shape: {X.shape}")
    print(f"Treatment shape: {T.shape}")
    print(f"Outcome shape: {Y.shape}")


if __name__ == "__main__":
    main()
