import warnings
warnings.filterwarnings("ignore", category=FutureWarning)

from pathlib import Path

import pandas as pd
from dowhy import CausalModel


def main():
    # Load dataset
    data_path = (
        Path(__file__).resolve().parents[2]
        / "data"
        / "pricing_data.csv"
    )

    if not data_path.exists():
        raise FileNotFoundError(f"Dataset not found: {data_path}")

    df = pd.read_csv(data_path)

    required = [
        "discount",
        "purchase",
        "price",
        "competitor_price",
        "promotion",
        "season",
    ]

    missing = sorted(set(required) - set(df.columns))
    if missing:
        raise ValueError(f"Missing columns: {missing}")

    df = df[required].dropna().copy()

    if df.empty:
        raise ValueError("Dataset is empty.")

    if not df["discount"].between(0, 0.35).all():
        raise ValueError("Discount must be between 0 and 0.35.")

    if not df["purchase"].isin([0, 1]).all():
        raise ValueError("Purchase must contain only 0 and 1.")

    # Corrected DAG for the synthetic data generator
    graph = """
    digraph {
        price -> competitor_price;
        price -> purchase;
        competitor_price -> purchase;
        promotion -> purchase;
        season -> purchase;
        discount -> purchase;
    }
    """

    # Build causal model
    model = CausalModel(
        data=df,
        treatment="discount",
        outcome="purchase",
        graph=graph,
    )

    # Identify causal effect
    estimand = model.identify_effect()

    # Estimate ATE
    estimate = model.estimate_effect(
        estimand,
        method_name="backdoor.linear_regression",
        method_params={"fit_intercept": True},
    )

    print("\n========== CAUSAL MODEL ==========")
    print(f"Dataset rows      : {len(df)}")
    print("Treatment         : discount")
    print("Outcome           : purchase")
    print("DAG               : Identified")
    print(f"Estimated ATE     : {estimate.value:.6f}")

    # Random common cause test
    result1 = model.refute_estimate(
        estimand,
        estimate,
        method_name="random_common_cause",
    )

    # Placebo treatment test
    result2 = model.refute_estimate(
        estimand,
        estimate,
        method_name="placebo_treatment_refuter",
        placebo_type="permute",
    )

    print("\n========== REFUTATION RESULTS ==========")

    print("\n1. Random Common Cause")
    print(f"Original estimate : {result1.estimated_effect:.6f}")
    print(f"New estimate      : {result1.new_effect:.6f}")

    print("\n2. Placebo Treatment")
    print(f"Original estimate : {result2.estimated_effect:.6f}")
    print(f"Placebo estimate  : {result2.new_effect:.6f}")

    print("\n========== SUMMARY ==========")
    print("Both refutation procedures completed.")
    print("See estimates above to assess their stability.")
    print("These tests do not prove causal validity.")


if __name__ == "__main__":
    main()
