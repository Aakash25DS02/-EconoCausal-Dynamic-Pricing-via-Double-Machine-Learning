

import numpy as np
import pandas as pd
from scipy.optimize import LinearConstraint
from scipy.sparse import lil_matrix


def build_constraints(
    offers: pd.DataFrame,
    budget: float,
) -> LinearConstraint:
    """Build customer exclusivity and budget constraints."""
    if not np.isfinite(budget) or budget < 0:
        raise ValueError("Budget must be finite and nonnegative.")

    required = {"customer_id", "discount_amount"}
    missing = required - set(offers.columns)

    if missing:
        raise ValueError(f"Missing columns: {sorted(missing)}")

    if offers["customer_id"].isna().any():
        raise ValueError("customer_id cannot be missing.")

    if offers["discount_amount"].isna().any():
        raise ValueError("discount_amount cannot be missing.")

    costs = pd.to_numeric(
        offers["discount_amount"], errors="raise"
    ).to_numpy(dtype=float)

    if not np.isfinite(costs).all() or (costs < 0).any():
        raise ValueError(
            "Discount costs must be finite and nonnegative."
        )

    n = len(offers)
    if n == 0:
        raise ValueError("No offers provided.")

    customer_codes, _ = pd.factorize(offers["customer_id"])
    unique_customers = int(customer_codes.max()) + 1

    # One row per customer, plus one budget row.
    matrix = lil_matrix((unique_customers + 1, n), dtype=float)

    for col, customer_code in enumerate(customer_codes):
        matrix[customer_code, col] = 1

    matrix[unique_customers, :] = costs

    lower = np.full(unique_customers + 1, -np.inf)
    upper = np.concatenate([
        np.ones(unique_customers),
        [budget],
    ])

    return LinearConstraint(
        matrix.tocsr(), lb=lower, ub=upper
    )
