
import numpy as np
import pandas as pd
from scipy.optimize import Bounds, milp

from .objective import build_objective
from .constraints import build_constraints


def optimize_discounts(
    offers: pd.DataFrame,
    budget: float,
) -> dict:
    """Select offers to maximize total incremental profit."""
    required = {
        "customer_id",
        "discount_amount",
        "incremental_profit",
    }
    missing = required - set(offers.columns)

    if missing:
        raise ValueError(f"Missing columns: {sorted(missing)}")

    if "eligible" in offers.columns:
        eligible = offers["eligible"].fillna(False).astype(bool)
        offers = offers.loc[eligible].copy()
    else:
        offers = offers.copy()

    if offers.empty:
        return {
            "selected_offers": offers.copy(),
            "total_discount_spend": 0.0,
            "total_incremental_profit": 0.0,
            "budget": float(budget),
            "remaining_budget": float(budget),
            "status": "no_eligible_offers",
        }

    costs = pd.to_numeric(
        offers["discount_amount"], errors="raise"
    ).to_numpy(dtype=float)

    if not np.isfinite(costs).all() or (costs < 0).any():
        raise ValueError("Discount costs must be finite and nonnegative.")

    if not np.isfinite(budget) or budget < 0:
        raise ValueError("Budget must be finite and nonnegative.")

    objective = build_objective(offers)
    constraints = build_constraints(offers, budget)

    result = milp(
        c=objective,
        integrality=np.ones(len(offers)),
        bounds=Bounds(
            np.zeros(len(offers)),
            np.ones(len(offers)),
        ),
        constraints=constraints,
        options={"disp": False},
    )

    if result.status != 0 or result.x is None:
        raise RuntimeError(
            f"Optimization did not reach an optimal solution: {result.message}"
        )

    selected_mask = result.x > 0.5
    selected = offers.iloc[np.flatnonzero(selected_mask)].copy()

    total_spend = float(selected["discount_amount"].sum())
    total_profit = float(selected["incremental_profit"].sum())

    if total_spend > budget + 1e-6:
        raise RuntimeError("Optimizer returned a solution exceeding budget.")

    return {
        "selected_offers": selected,
        "total_discount_spend": total_spend,
        "total_incremental_profit": total_profit,
        "budget": float(budget),
        "remaining_budget": float(budget - total_spend),
        "status": "optimal",
    }

    
if __name__ == "__main__":
    sample_offers = pd.DataFrame({
        "customer_id": ["C001", "C002", "C003"],
        "discount_amount": [100, 200, 100],
        "incremental_profit": [80, 150, 60],
        "eligible": [True, True, True],
    })

    result = optimize_discounts(sample_offers, budget=200)

    print("Selected offers:")
    print(result["selected_offers"])
    print("Spend:", result["total_discount_spend"])
    print("Incremental profit:", result["total_incremental_profit"])
    print("Status:", result["status"])
