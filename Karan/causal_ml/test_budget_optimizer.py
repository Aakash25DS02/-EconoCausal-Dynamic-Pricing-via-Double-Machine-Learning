from pathlib import Path

import pandas as pd


def test_optimized_discounts():
    root = Path(__file__).resolve().parents[2]
    input_path = root / "data" / "treatment_effects.csv"
    output_path = root / "data" / "optimized_discounts.csv"

    source = pd.read_csv(input_path)
    result = pd.read_csv(output_path)

    assert len(result) == len(source), "Row count changed"
    assert result["optimized_discount"].notna().all(), "Missing discounts"
    assert result["optimized_discount"].between(0.0, 0.35).all(), (
        "Discount outside 0–35% bounds"
    )
    assert result["optimized_discount"].sum() <= (
        source["discount"].sum() + 1e-5
    ), "Budget constraint exceeded"

    print("All optimizer validation checks passed.")


if __name__ == "__main__":
    test_optimized_discounts()
