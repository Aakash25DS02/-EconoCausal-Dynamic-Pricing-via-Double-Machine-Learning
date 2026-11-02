


import numpy as np
import pandas as pd


def build_objective(offers: pd.DataFrame) -> np.ndarray:
    """Return negative incremental profit for minimization."""
    if "incremental_profit" not in offers.columns:
        raise ValueError(
            "Offers must contain incremental_profit."
        )

    profits = pd.to_numeric(
        offers["incremental_profit"], errors="raise"
    ).to_numpy(dtype=float)

    if not np.isfinite(profits).all():
        raise ValueError(
            "incremental_profit must contain finite values."
        )

    return -profits
