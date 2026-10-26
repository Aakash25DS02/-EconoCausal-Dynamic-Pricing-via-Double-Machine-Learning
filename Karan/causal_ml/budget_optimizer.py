from pathlib import Path

import numpy as np
import pandas as pd
from scipy.optimize import minimize


def main():
    root = Path(__file__).resolve().parents[2]
    input_path = root / "data" / "treatment_effects.csv"
    output_path = root / "data" / "optimized_discounts.csv"

    df = pd.read_csv(input_path)
    required = {"discount", "estimated_effect"}
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"Missing required columns: {sorted(missing)}")

    df = df.dropna(subset=["discount", "estimated_effect"]).copy()
    df = df[
        np.isfinite(df["discount"]) & np.isfinite(df["estimated_effect"])
    ].reset_index(drop=True)

    if df.empty:
        raise ValueError("No valid treatment-effect rows found.")

    effects = df["estimated_effect"].to_numpy(dtype=float)
    initial = df["discount"].to_numpy(dtype=float)

    # Assumption: total allocated discount fractions cannot exceed
    # the sum of the historical discount fractions.
    budget = float(initial.sum())
    max_discount = 0.35

    # The effect estimates are for a +0.10 discount change.
    # This is a simplified allocation proxy, not a profit/revenue model.
    objective = lambda discounts: -float(
        np.dot(discounts / 0.10, effects)
    )

    result = minimize(
        objective,
        x0=np.clip(initial, 0.0, max_discount),
        method="SLSQP",
        bounds=[(0.0, max_discount)] * len(df),
        constraints=[{
            "type": "ineq",
            "fun": lambda discounts: budget - float(discounts.sum()),
        }],
        options={"maxiter": 1000, "ftol": 1e-9},
    )

    if not result.success:
        raise RuntimeError(f"Optimization failed: {result.message}")

    df["optimized_discount"] = result.x
    df["discount_change"] = df["optimized_discount"] - df["discount"]

    df.to_csv(output_path, index=False)

    print("Discount allocation optimization completed.")
    print(f"Rows optimized: {len(df)}")
    print(f"Discount budget (fraction-sum proxy): {budget:.4f}")
    print(f"Budget used: {result.x.sum():.4f}")
    print(f"Budget remaining: {budget - result.x.sum():.6f}")
    print(f"Rows receiving a discount: {(result.x > 0).sum()}")
    print(f"Rows at the 35% cap: {np.isclose(result.x, max_discount).sum()}")
    print("Note: this is a simplified effect-based proxy, not profit maximization.")
    print(f"Saved results to: {output_path}")


if __name__ == "__main__":
    main()