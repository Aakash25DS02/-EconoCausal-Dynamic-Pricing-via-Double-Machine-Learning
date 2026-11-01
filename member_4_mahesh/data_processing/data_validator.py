

import numpy as np
import pandas as pd

from member_4_mahesh.data_processing.data_loader import get_project_root


REQUIRED_COLUMNS = [
    "customer_id",
    "age",
    "tenure_months",
    "past_purchases",
    "avg_order_value",
    "days_since_last_purchase",
    "website_visits_30d",
    "cart_abandonment_rate",
    "support_tickets_90d",
    "price_sensitivity",
    "treatment",
    "discount_amount",
    "churned",
    "purchased_again",
    "revenue",
    "profit",
]

NUMERIC_COLUMNS = [
    col for col in REQUIRED_COLUMNS
    if col != "customer_id"
]

BINARY_COLUMNS = [
    "treatment",
    "churned",
    "purchased_again",
]


def validate_dataset(df: pd.DataFrame) -> dict:
    """Validate the retail dataset and return a report."""
    errors = []
    warnings = []

    missing_columns = sorted(
        set(REQUIRED_COLUMNS) - set(df.columns)
    )

    if missing_columns:
        raise ValueError(
            f"Missing required columns: {missing_columns}"
        )

    df = df.copy()

    if df.empty:
        raise ValueError("Dataset is empty.")

    if df["customer_id"].isna().any():
        errors.append("customer_id contains missing values.")

    if df["customer_id"].duplicated().any():
        errors.append("customer_id contains duplicate values.")

    # Convert numeric columns and detect invalid values.
    for col in NUMERIC_COLUMNS:
        converted = pd.to_numeric(df[col], errors="coerce")

        if converted.isna().any():
            errors.append(
                f"{col} contains missing or non-numeric values."
            )
        elif not np.isfinite(converted.to_numpy(dtype=float)).all():
            errors.append(f"{col} contains infinite values.")
        else:
            df[col] = converted

    if not errors:
        if not df["age"].between(18, 100).all():
            errors.append("age must be between 18 and 100.")

        if (df["tenure_months"] < 1).any():
            errors.append("tenure_months must be at least 1.")

        nonnegative_columns = [
            "past_purchases",
            "days_since_last_purchase",
            "website_visits_30d",
            "support_tickets_90d",
            "discount_amount",
            "revenue",
        ]

        for col in nonnegative_columns:
            if (df[col] < 0).any():
                errors.append(f"{col} cannot be negative.")

        if (df["avg_order_value"] <= 0).any():
            errors.append("avg_order_value must be positive.")

        for col in [
            "cart_abandonment_rate",
            "price_sensitivity",
        ]:
            if not df[col].between(0, 1).all():
                errors.append(f"{col} must be between 0 and 1.")

        for col in BINARY_COLUMNS:
            if not df[col].isin([0, 1]).all():
                errors.append(f"{col} must contain only 0 or 1.")

        treated = df["treatment"] == 1
        untreated = df["treatment"] == 0

        if (df.loc[untreated, "discount_amount"] != 0).any():
            errors.append(
                "Untreated customers must have discount_amount = 0."
            )

        if (df.loc[treated, "discount_amount"] <= 0).any():
            errors.append(
                "Treated customers must have a positive discount."
            )

        if (
            df["churned"] + df["purchased_again"] != 1
        ).any():
            errors.append(
                "churned and purchased_again must be complementary."
            )

    if df["treatment"].nunique() < 2:
        warnings.append(
            "Only one treatment group exists; causal estimation "
            "may not be possible."
        )

    if df["churned"].nunique() < 2:
        warnings.append(
            "Only one churn outcome class exists."
        )

    if errors:
        raise ValueError(
            "Dataset validation failed:\n- "
            + "\n- ".join(errors)
        )

    return {
        "valid": True,
        "rows": len(df),
        "columns": len(df.columns),
        "warnings": warnings,
    }


if __name__ == "__main__":
    # Example: Load your dataset (replace with your actual file path)
    import sys
    
    file_path = (
                get_project_root()
                / "member_4_mahesh"
                / "shared"
                / "data"
                / "raw"
                / "retail_customers.csv"
            )
    
    try:
        df = pd.read_csv(file_path)
        report = validate_dataset(df)
        print("Validation Successful! Report:")
        print(report)
    except FileNotFoundError:
        print(f"Error: Could not find file at '{file_path}'. Please update the path.")
    except Exception as e:
        print(e)