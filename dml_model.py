
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.base import clone
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestRegressor
from sklearn.impute import SimpleImputer
from sklearn.model_selection import KFold, cross_val_predict
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import OneHotEncoder


DATA_PATH = Path(__file__).resolve().parent / "data" / "pricing_data.csv"


def estimate_discount_effect():
    df = pd.read_csv(DATA_PATH)

    required = {
        "discount",
        "purchase",
        "price",
        "competitor_price",
        "promotion",
        "season",
    }
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"Missing required columns: {sorted(missing)}")

    if df[list(required)].isna().any().any():
        raise ValueError("Required model columns contain missing values.")

    if not set(df["purchase"].unique()).issubset({0, 1}):
        raise ValueError("purchase must contain only 0 and 1.")

    # Controls follow the observed variables in the synthetic generator.
    # The competitor-to-price ratio is included because it enters the
    # generator's purchase-probability formula.
    X = pd.DataFrame({
        "price": df["price"].astype(float),
        "competitor_ratio": (
            df["competitor_price"].astype(float)
            / df["price"].astype(float)
        ),
        "promotion": df["promotion"].astype(float),
        "season": df["season"].astype(str),
    })

    treatment = df["discount"].astype(float).to_numpy()
    outcome = df["purchase"].astype(float).to_numpy()

    numeric = ["price", "competitor_ratio", "promotion"]
    categorical = ["season"]

    preprocessor = ColumnTransformer([
        (
            "num",
            SimpleImputer(strategy="median"),
            numeric,
        ),
        (
            "cat",
            make_pipeline(
                SimpleImputer(strategy="most_frequent"),
                OneHotEncoder(handle_unknown="ignore"),
            ),
            categorical,
        ),
    ])

    outcome_model = make_pipeline(
        clone(preprocessor),
        RandomForestRegressor(
            n_estimators=200,
            min_samples_leaf=10,
            random_state=42,
            n_jobs=-1,
        ),
    )

    treatment_model = make_pipeline(
        clone(preprocessor),
        RandomForestRegressor(
            n_estimators=200,
            min_samples_leaf=10,
            random_state=43,
            n_jobs=-1,
        ),
    )

    cv = KFold(n_splits=5, shuffle=True, random_state=42)

    y_hat = cross_val_predict(
        outcome_model, X, outcome, cv=cv, method="predict"
    )
    t_hat = cross_val_predict(
        treatment_model, X, treatment, cv=cv, method="predict"
    )

    y_residual = outcome - y_hat
    t_residual = treatment - t_hat

    denominator = float(np.dot(t_residual, t_residual))
    if denominator < 1e-10:
        raise ValueError(
            "Insufficient discount variation after accounting for controls."
        )

    effect = float(np.dot(t_residual, y_residual) / denominator)

    if not np.isfinite(effect):
        raise ValueError("The estimated effect is not finite.")

    return {
        "method": "Cross-fitted residual-on-residual DML-style estimate",
        "treatment": "discount",
        "outcome": "purchase",
        "estimated_effect_per_1_0_discount": effect,
        "estimated_effect_per_0_01_discount": effect * 0.01,
        "observations": len(df),
        "purchase_rate": float(outcome.mean()),
        "validation": "passed",
        "interpretation": (
            "Model-based estimate of the change in purchase probability "
            "per unit increase in discount, conditional on the selected "
            "controls. Causal interpretation requires appropriate "
            "identification assumptions."
        ),
    }


if __name__ == "__main__":
    print(estimate_discount_effect())
