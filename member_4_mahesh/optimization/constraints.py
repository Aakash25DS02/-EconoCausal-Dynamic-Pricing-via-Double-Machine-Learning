
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
    