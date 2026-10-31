from pathlib import Path

import pandas as pd
from dowhy import CausalModel


def main():
    data_path = Path(__file__).resolve().parents[2] / "data" / "pricing_data.csv"
    df = pd.read_csv(data_path)

    required = [
        "discount", "purchase", "price",
        "competitor_price", "promotion", "season"
    ]
    df = df[required].dropna().copy()

    # Encode season as numeric dummy variables for refutation compatibility.
    df = pd.get_dummies(df, columns=["season"], drop_first=True, dtype=int)

    confounders = [
        "price", "competitor_price", "promotion"
    ] + [c for c in df.columns if c.startswith("season_")]

    graph_edges = " ".join(
        f"{c} -> discount; {c} -> purchase;" for c in confounders
    )
    graph = f"digraph {{ {graph_edges} discount -> purchase; }}"

    model = CausalModel(
        data=df,
        treatment="discount",
        outcome="purchase",
        graph=graph,
    )

    estimand = model.identify_effect()
    estimate = model.estimate_effect(
    estimand,
    method_name="backdoor.linear_regression",
    method_params={"fit_intercept": True},
)

    print("Estimated ATE:", estimate.value)

    print("\nRunning random-common-cause refutation...")
    result1 = model.refute_estimate(
        estimand,
        estimate,
        method_name="random_common_cause",
    )
    print(result1)

    print("\nRunning placebo-treatment refutation...")
    result2 = model.refute_estimate(
        estimand,
        estimate,
        method_name="placebo_treatment_refuter",
        placebo_type="permute",
    )
    print(result2)


if __name__ == "__main__":
    main()