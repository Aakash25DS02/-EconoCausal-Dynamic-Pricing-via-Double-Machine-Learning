from pathlib import Path

import numpy as np
import pandas as pd


def test_optimized_discounts():
    root = Path(__file__).resolve().parents[2]
    input_path = root / "data" / "treatment_effects.csv"
    output_path = root / "data" / "optimized_discounts.csv"

    source = pd.read_csv(input_path)
    result = pd.read_csv(output_path)

    # Check output row count
    assert len(result) == len(source), "Row count changed"

    # Check required columns
    required = {
        "discount",
        "estimated_effect",
        "optimized_discount",
        "discount_change",
    }
    missing = required - set(result.columns)
    assert not missing, f"Missing columns: {sorted(missing)}"

    # Check for missing and non-finite values
    numeric_cols = ["discount", "estimated_effect", "optimized_discount"]
    assert result[numeric_cols].notna().all().all(), (
        "Missing values found in optimization results"
    )
    assert np.isfinite(result[numeric_cols].to_numpy(dtype=float)).all(), (
        "Non-finite values found in optimization results"
    )

    # Check discount bounds: 0% to 35%
    assert result["optimized_discount"].between(0.0, 0.35).all(), (
        "Optimized discount outside 0–35% bounds"
    )

    # Check total discount budget constraint
    budget = source["discount"].sum()
    allocated = result["optimized_discount"].sum()
    assert allocated <= budget + 1e-5, "Budget constraint exceeded"

    # Check negative-effect rows receive zero optimized discount
    negative_effect_rows = result[result["estimated_effect"] < 0]
    assert (
        negative_effect_rows["optimized_discount"] <= 1e-8
    ).all(), "Negative-effect rows should receive zero optimized discount"

    # Check discount change calculation
    expected_change = result["optimized_discount"] - result["discount"]
    assert np.allclose(
        result["discount_change"], expected_change, atol=1e-8
    ), "Discount changes are incorrect"

    print("All optimizer validation checks passed.")


if __name__ == "__main__":
    test_optimized_discounts()