
from pathlib import Path

import pandas as pd
from dowhy import CausalModel


def main():
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

    # DAG reflecting the synthetic data-generation process.
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

    model = CausalModel(
        data=df,
        treatment="discount",
        outcome="purchase",
        graph=graph,
    )

    estimand = model.identify_effect()

    print("========== CORRECTED CAUSAL DAG ==========")
    print("Treatment: discount")
    print("Outcome: purchase")

    print("\nDiscount assignment:")
    print("Random continuous assignment between 0 and 0.35")

    print("\nAdjustment assumptions:")
    print("No confounders of discount and purchase")
    print("based on the synthetic data generator.")

    print("\nIdentified estimand:")
    print(estimand)

    print(
        "\nNote: This DAG represents the synthetic "
        "data-generation mechanism, not necessarily "
        "a real-world pricing process."
    )


if __name__ == "__main__":
    main()
