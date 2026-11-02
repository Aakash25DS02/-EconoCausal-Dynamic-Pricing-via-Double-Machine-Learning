"""Reusable EconML causal pricing service for API integration."""

from pathlib import Path

import numpy as np
import pandas as pd
from econml.dml import LinearDML
from sklearn.ensemble import RandomForestRegressor

try:
    from .validate_pricing_data import validate_pricing_data
except ImportError:
    from validate_pricing_data import validate_pricing_data


FEATURE_COLUMNS = [
    "price",
    "competitor_price",
    "promotion",
    "season",
]

MIN_DISCOUNT = 0.0
MAX_DISCOUNT = 0.35


def build_feature_matrix(df, feature_columns=None):
    """Build the same numeric feature matrix for training and inference."""
    missing = set(FEATURE_COLUMNS) - set(df.columns)
    if missing:
        raise ValueError(f"Missing feature columns: {sorted(missing)}")

    X = pd.get_dummies(
        df[FEATURE_COLUMNS],
        columns=["season"],
        drop_first=True,
        dtype=float,
    )

    if feature_columns is not None:
        X = X.reindex(columns=feature_columns, fill_value=0.0)

    return X.astype(float)


class CausalPricingService:
    """Train a LinearDML model and estimate customer-level discount effects."""

    def __init__(self, random_state=42):
        self.random_state = random_state
        self.model = None
        self.feature_columns = None
        self.training_summary = None

    def fit(self, df):
        """Fit the causal model using the supplied historical pricing data."""
        required = {
            "customer_id",
            "price",
            "discount",
            "competitor_price",
            "promotion",
            "season",
            "purchase",
        }

        missing = required - set(df.columns)
        if missing:
            raise ValueError(f"Missing required columns: {sorted(missing)}")

        data = df.copy()

        if data.empty:
            raise ValueError("Training dataset is empty.")

        if data["customer_id"].isna().any():
            raise ValueError("Customer IDs cannot be missing.")

        if not data["customer_id"].is_unique:
            raise ValueError("Customer IDs must be unique for customer-level ITE.")

        if not validate_pricing_data(data):
            raise ValueError("Pricing dataset validation failed.")

        if data["discount"].nunique() < 2:
            raise ValueError("Discount treatment must contain variation.")

        if data["purchase"].nunique() < 2:
            raise ValueError("Purchase outcome must contain both 0 and 1.")

        X = build_feature_matrix(data)
        T = data["discount"].astype(float)
        Y = data["purchase"].astype(float)

        if not np.isfinite(X.to_numpy()).all():
            raise ValueError("Feature matrix contains non-finite values.")

        self.model = LinearDML(
            model_y=RandomForestRegressor(
                n_estimators=100,
                min_samples_leaf=10,
                random_state=self.random_state,
                n_jobs=-1,
            ),
            model_t=RandomForestRegressor(
                n_estimators=100,
                min_samples_leaf=10,
                random_state=self.random_state,
                n_jobs=-1,
            ),
            discrete_treatment=False,
            random_state=self.random_state,
        )

        self.model.fit(Y, T, X=X)

        self.feature_columns = list(X.columns)

        self.training_summary = {
            "rows_used": int(len(data)),
            "unique_customers": int(data["customer_id"].nunique()),
            "mean_purchase_rate": float(Y.mean()),
            "minimum_discount": float(T.min()),
            "maximum_discount": float(T.max()),
            "feature_count": int(X.shape[1]),
            "model": "EconML LinearDML",
        }

        return self

    def estimate_ite(self, customers, reference_discount=0.0,
                     target_discount=0.10):
        """
        Estimate the effect of changing discount from reference to target.

        Default comparison: 0% discount versus 10% discount.
        Effects are changes in predicted purchase probability.
        """
        if self.model is None:
            raise RuntimeError("Call fit() before estimate_ite().")

        if not MIN_DISCOUNT <= reference_discount <= MAX_DISCOUNT:
            raise ValueError("Reference discount must be between 0 and 0.35.")

        if not MIN_DISCOUNT <= target_discount <= MAX_DISCOUNT:
            raise ValueError("Target discount must be between 0 and 0.35.")

        if target_discount <= reference_discount:
            raise ValueError("Target discount must exceed reference discount.")

        if "customer_id" not in customers.columns:
            raise ValueError("Inference data must contain customer_id.")

        if customers["customer_id"].isna().any():
            raise ValueError("Customer IDs cannot be missing.")

        if not customers["customer_id"].is_unique:
            raise ValueError("Customer IDs must be unique.")

        X = build_feature_matrix(customers, self.feature_columns)

        effects = np.asarray(
            self.model.effect(
                X,
                T0=reference_discount,
                T1=target_discount,
            )
        ).reshape(-1)

        if len(effects) != len(customers):
            raise RuntimeError("Unexpected number of treatment-effect estimates.")

        if not np.isfinite(effects).all():
            raise RuntimeError("Model generated non-finite treatment effects.")

        results = pd.DataFrame({
            "customer_id": customers["customer_id"].to_numpy(),
            "reference_discount": reference_discount,
            "target_discount": target_discount,
            "estimated_effect": effects,
        })

        return results

    def summarize(self, results):
        """Return a JSON-friendly summary of estimated treatment effects."""
        effects = results["estimated_effect"].to_numpy(dtype=float)

        if len(effects) == 0 or not np.isfinite(effects).all():
            raise ValueError("Cannot summarize empty or invalid estimates.")

        return {
            "customer_count": int(len(effects)),
            "mean_effect": float(np.mean(effects)),
            "median_effect": float(np.median(effects)),
            "std_effect": float(np.std(effects)),
            "minimum_effect": float(np.min(effects)),
            "maximum_effect": float(np.max(effects)),
            "positive_effect_customers": int((effects > 0).sum()),
            "negative_effect_customers": int((effects < 0).sum()),
        }


def run_causal_analysis(
    data_path,
    output_path,
    reference_discount=0.0,
    target_discount=0.10,
):
    """Run the complete causal service and save customer-level estimates."""
    data_path = Path(data_path)
    output_path = Path(output_path)

    if not data_path.exists():
        raise FileNotFoundError(f"Dataset not found: {data_path}")

    customers = pd.read_csv(data_path)

    service = CausalPricingService()
    service.fit(customers)

    results = service.estimate_ite(
        customers,
        reference_discount=reference_discount,
        target_discount=target_discount,
    )

    summary = service.summarize(results)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    results.to_csv(output_path, index=False)

    return {
        "training": service.training_summary,
        "treatment_effect_summary": summary,
        "output_path": str(output_path),
        "results": results,
    }


if __name__ == "__main__":
    project_root = Path(__file__).resolve().parents[2]

    report = run_causal_analysis(
        project_root / "data" / "pricing_data.csv",
        project_root / "data" / "treatment_effects_week4.csv",
    )

    print("\n=== CAUSAL SERVICE TRAINING ===")
    print(report["training"])

    print("\n=== CUSTOMER TREATMENT EFFECT SUMMARY ===")
    print(report["treatment_effect_summary"])

    print(f"\nSaved results to: {report['output_path']}")
