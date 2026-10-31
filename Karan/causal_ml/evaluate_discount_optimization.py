from pathlib import Path

import numpy as np
import pandas as pd


def main():
    root = Path(__file__).resolve().parents[2]
    input_path = root / "data" / "optimized_discounts.csv"
    output_path = root / "data" / "discount_optimization_report.csv"

    df = pd.read_csv(input_path)

    required = {"discount", "estimated_effect", "optimized_discount"}
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"Missing columns: {sorted(missing)}")

    df = df.dropna(
        subset=["discount", "estimated_effect", "optimized_discount"]
    ).copy()

    if df.empty:
        raise ValueError("No valid rows available for evaluation.")

    if not np.isfinite(
        df[["discount", "estimated_effect", "optimized_discount"]].to_numpy()
    ).all():
        raise ValueError("Input contains non-finite values.")

    if not df["discount"].between(0, 1).all():
        raise ValueError("Original discounts must be between 0 and 1.")

    if not df["optimized_discount"].between(0, 0.35).all():
        raise ValueError("Optimized discounts must be between 0 and 0.35.")

    df["discount_change"] = df["optimized_discount"] - df["discount"]
    df["estimated_effect_proxy"] = (
        df["optimized_discount"] / 0.10
    ) * df["estimated_effect"]

    summary = pd.DataFrame(
        {
            "metric": [
                "rows_evaluated",
                "original_mean_discount",
                "optimized_mean_discount",
                "original_total_discount_fraction",
                "optimized_total_discount_fraction",
                "mean_absolute_discount_change",
                "rows_discount_increased",
                "rows_discount_decreased",
                "rows_discount_unchanged",
                "rows_at_35_percent_cap",
                "sum_estimated_effect_proxy",
            ],
            "value": [
                len(df),
                df["discount"].mean(),
                df["optimized_discount"].mean(),
                df["discount"].sum(),
                df["optimized_discount"].sum(),
                df["discount_change"].abs().mean(),
                (df["discount_change"] > 1e-9).sum(),
                (df["discount_change"] < -1e-9).sum(),
                (df["discount_change"].abs() <= 1e-9).sum(),
                np.isclose(df["optimized_discount"], 0.35).sum(),
                df["estimated_effect_proxy"].sum(),
            ],
        }
    )

    summary.to_csv(output_path, index=False)

    print("Discount optimization evaluation completed.")
    print(summary.to_string(index=False))
    print(f"\nSaved report to: {output_path}")
    print(
        "\nNote: the effect proxy is not measured revenue or profit. "
        "It should not be interpreted as a validated business outcome."
    )


if __name__ == "__main__":
    main()