
from pathlib import Path

import pandas as pd
from sklearn.ensemble import RandomForestRegressor, RandomForestClassifier
from sklearn.model_selection import cross_val_predict
from sklearn.base import clone
from sklearn.model_selection import KFold, StratifiedKFold
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import make_pipeline
from sklearn.impute import SimpleImputer
from sklearn.metrics import mean_squared_error


DATA_PATH = Path(__file__).resolve().parent / "data" / "pricing_data.csv"


def estimate_discount_effect():
    df = pd.read_csv(DATA_PATH)

    # Treatment: discount; Outcome: purchase
    # Controls: observed customer, competitor, and promotion characteristics
    treatment = df["discount"].astype(float)
    outcome = df["purchase"].astype(float)

    feature_cols = [
        "price",
        "competitor_price",
        "promotion",
        "season",
    ]
    X = df[feature_cols].copy()

    # Encode categorical variables such as season.
    categorical = ["season"]
    numeric = [c for c in feature_cols if c not in categorical]

    preprocessor = ColumnTransformer(
        transformers=[
            ("num", SimpleImputer(strategy="median"), numeric),
            (
                "cat",
                make_pipeline(
                    SimpleImputer(strategy="most_frequent"),
                    OneHotEncoder(handle_unknown="ignore"),
                ),
                categorical,
            ),
        ]
    )

    # Cross-fitting: predict outcome and treatment using controls.
    outcome_model = make_pipeline(
        preprocessor,
        RandomForestRegressor(n_estimators=100, min_samples_leaf=10, random_state=42),
    )
    treatment_model = make_pipeline(
        preprocessor,
        RandomForestRegressor(n_estimators=100, min_samples_leaf=10, random_state=42),
    )

    y_hat = cross_val_predict(
        clone(outcome_model), X, outcome, cv=5, method="predict"
    )
    t_hat = cross_val_predict(
        clone(treatment_model), X, treatment, cv=5, method="predict"
    )

    # Residual-on-residual estimate.
    y_residual = outcome - y_hat
    t_residual = treatment - t_hat

    denominator = (t_residual**2).sum()
    if denominator < 1e-10:
        raise ValueError("Insufficient variation in discount after controls.")

    effect = float((t_residual * y_residual).sum() / denominator)

    return {
        "method": "Cross-fitted residual-on-residual DML-style estimate",
        "treatment": "discount",
        "outcome": "purchase",
        "estimated_effect_per_1_0_discount": effect,
        "estimated_effect_per_0_01_discount": effect * 0.01,
        "observations": len(df),
        "interpretation": (
            "The estimate is the change in purchase probability for a "
            "1.0 increase in the discount fraction, conditional on the "
            "observed controls. It is not automatically causal without "
            "appropriate identification assumptions."
        ),
    }


if __name__ == "__main__":
    print(estimate_discount_effect())
