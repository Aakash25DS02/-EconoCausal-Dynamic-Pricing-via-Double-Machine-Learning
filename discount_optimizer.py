
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestClassifier
from sklearn.impute import SimpleImputer
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import OneHotEncoder


DATA_PATH = Path(__file__).resolve().parent / "data" / "pricing_data.csv"

FEATURES = [
    "price",
    "discount",
    "competitor_price",
    "promotion",
    "season",
]


def recommend_discount():
    if not DATA_PATH.exists():
        raise FileNotFoundError(f"Dataset not found: {DATA_PATH}")

    df = pd.read_csv(DATA_PATH)

    required = FEATURES + ["purchase"]
    missing = set(required) - set(df.columns)
    if missing:
        raise ValueError(f"Missing required columns: {sorted(missing)}")

    if df.empty or df[required].isna().any().any():
        raise ValueError("Dataset is empty or contains missing model values.")

    if not set(df["purchase"].unique()).issubset({0, 1}):
        raise ValueError("purchase must contain only 0 and 1.")

    numeric_features = [
        "price",
        "discount",
        "competitor_price",
        "promotion",
    ]

    preprocessor = ColumnTransformer([
        (
            "numeric",
            SimpleImputer(strategy="median"),
            numeric_features,
        ),
        (
            "season",
            make_pipeline(
                SimpleImputer(strategy="most_frequent"),
                OneHotEncoder(handle_unknown="ignore"),
            ),
            ["season"],
        ),
    ])

    model = make_pipeline(
        preprocessor,
        RandomForestClassifier(
            n_estimators=200,
            min_samples_leaf=10,
            random_state=42,
            n_jobs=-1,
        ),
    )

    X = df[FEATURES].copy()
    y = df["purchase"].astype(int)
    model.fit(X, y)

    candidates = np.round(np.arange(0.0, 0.351, 0.01), 2)
    results = []

    for discount in candidates:
        scenario = X.copy()
        scenario["discount"] = discount

        probabilities = model.predict_proba(scenario)[:, 1]
        effective_prices = scenario["price"] * (1 - discount)

        results.append({
            "discount": float(discount),
            "predicted_purchase_probability": float(
                probabilities.mean()
            ),
            "estimated_revenue_per_record": float(
                (effective_prices * probabilities).mean()
            ),
        })

    best = max(
        results,
        key=lambda item: item["estimated_revenue_per_record"],
    )

    return {
        "method": "Predictive discount scenario comparison",
        "objective": "Estimated revenue per record, not profit",
        "observations": len(df),
        "recommended_discount": best["discount"],
        "predicted_purchase_probability": best[
            "predicted_purchase_probability"
        ],
        "estimated_revenue_per_record": best[
            "estimated_revenue_per_record"
        ],
        "scenarios_evaluated": len(results),
        "note": (
            "Model-based scenario recommendation, not a proven causal "
            "effect or a guarantee of real-world revenue."
        ),
        "all_scenarios": results,
    }


if __name__ == "__main__":
    print(recommend_discount())
