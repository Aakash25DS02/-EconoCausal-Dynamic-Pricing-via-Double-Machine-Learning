from pathlib import Path

import numpy as np
import pandas as pd
from scipy.optimize import minimize


def main():
    project_root = Path(__file__).resolve().parents[2]
    input_path = project_root / "data" / "treatment_effects.csv"

    df = pd.read_csv(input_path)
    df = df.dropna(subset=["discount", "estimated_effect"]).copy()

    if df.empty:
        raise ValueError("No valid treatment-effect rows found.")

    # Simplified model: discount is the budget cost per customer.
    # The objective maximizes the sum of estimated effects, subject
    # to a total discount budget and each observed discount's bounds.
    effects = df["estimated_effect"].to_numpy(dtype=float)
    initial_discounts = df["discount"].to_numpy(dtype=float)

    budget = float(initial_discounts.sum())

    def objective(discounts):
        return -float(np.dot(discounts, effects))

    constraints = [
        {
            "type": "ineq",
            "fun": lambda discounts: budget - float(discounts.sum()),
        }
    ]

    result = minimize(
        objective,
        x0=initial_discounts,
        method="SLSQP",
        bounds=[(0.0, 0.35)] * len(df),
        constraints=constraints,
    )

    if not result.success:
        raise RuntimeError(f"Optimization failed: {result.message}")

    df["optimized_discount"] = result.x
    df["discount_change"] = (
    df["optimized_discount"] - df["discount"]
)

    output_path = project_root / "data" / "optimized_discounts.csv"
    df.to_csv(output_path, index=False)

    print("Budget optimization completed.")
    print(f"Customers/rows optimized: {len(df)}")
    print(f"Discount budget: {budget:.4f}")
    print(f"Optimized budget used: {result.x.sum():.4f}")
    print(f"Estimated effect objective: {-result.fun:.6f}")
    print(f"Results saved to: {output_path}")


if __name__ == "__main__":
    main()
