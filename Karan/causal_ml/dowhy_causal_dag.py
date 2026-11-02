from pathlib import Path

import pandas as pd
from dowhy import CausalModel


def main():
    data_path = Path(__file__).resolve().parents[2] / "data" / "pricing_data.csv"
    if not data_path.exists():
        raise FileNotFoundError(f"Dataset not found: {data_path}")

    df = pd.read_csv(data_path)
    required = [
        "discount", "purchase", "price",
        "competitor_price", "promotion", "season"
    ]
    missing = sorted(set(required) - set(df.columns))
    if missing:
        raise ValueError(f"Missing columns: {missing}")

    df = df[required].dropna().copy()

    graph = (
        "digraph { "
        "price -> discount; price -> purchase; "
        "competitor_price -> discount; competitor_price -> purchase; "
        "promotion -> discount; promotion -> purchase; "
        "season -> discount; season -> purchase; "
        "discount -> purchase; "
        "}"
    )

    model = CausalModel(
        data=df,
        treatment="discount",
        outcome="purchase",
        graph=graph,
    )
    estimand = model.identify_effect()

    print(f"Rows used: {len(df)}")
    print("Treatment: discount")
    print("Outcome: purchase")
    print("Proposed adjustment variables: price, competitor_price, promotion, season")
    print("\nIdentified estimand:")
    print(estimand)
    print("\nThe DAG encodes assumptions; it does not prove causality.")


if __name__ == "__main__":
    main()