from pathlib import Path

import pandas as pd

REQUIRED_COLUMNS = {
    "price",
    "discount",
    "competitor_price",
    "promotion",
    "season",
    "purchase",
}


def validate_pricing_data(df: pd.DataFrame) -> bool:
    """Validate pricing data before causal ML analysis."""
    errors = []

    missing_columns = REQUIRED_COLUMNS - set(df.columns)
    if missing_columns:
        errors.append(f"Missing required columns: {sorted(missing_columns)}")

    if missing_columns:
        for error in errors:
            print(f"ERROR: {error}")
        return False

    if df.empty:
        errors.append("Dataset is empty.")

    if df["price"].isna().any() or (df["price"] <= 0).any():
        errors.append("Price must be present and greater than zero.")

    if (
        df["competitor_price"].isna().any()
        or (df["competitor_price"] <= 0).any()
    ):
        errors.append("Competitor price must be present and greater than zero.")

    if (
        df["discount"].isna().any()
        or (~df["discount"].between(0, 1)).any()
    ):
        errors.append("Discount must be between 0 and 1.")

    if df["purchase"].isna().any() or not df["purchase"].isin([0, 1]).all():
        errors.append("Purchase must contain only 0 or 1, with no missing values.")

    if df["promotion"].isna().any() or not df["promotion"].isin([0, 1]).all():
        errors.append("Promotion must contain only 0 or 1, with no missing values.")

    if df["season"].isna().any():
        errors.append("Season must not contain missing values.")

    duplicate_count = int(df.duplicated().sum())
    if duplicate_count:
        errors.append(f"Found {duplicate_count} duplicate rows.")

    if errors:
        print("Dataset validation FAILED:")
        for error in errors:
            print(f"- {error}")
        return False

    print(f"Dataset validation PASSED: {len(df)} rows.")
    return True


if __name__ == "__main__":
    project_root = Path(__file__).resolve().parents[2]
    data_path = project_root / "data" / "pricing_data.csv"

    if not data_path.exists():
        raise FileNotFoundError(
            f"Dataset not found at {data_path}. "
            "Generate the dataset first or update the path."
        )

    data = pd.read_csv(data_path)
    valid = validate_pricing_data(data)
    raise SystemExit(0 if valid else 1)
