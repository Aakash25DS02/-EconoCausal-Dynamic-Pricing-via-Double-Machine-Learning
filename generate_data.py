
from pathlib import Path

import numpy as np
import pandas as pd


def generate_pricing_data(n: int = 2000, seed: int = 42) -> pd.DataFrame:
    rng = np.random.default_rng(seed)

    price = rng.uniform(100, 1000, n)
    discount = rng.uniform(0, 0.35, n)
    competitor_price = price * rng.uniform(0.8, 1.2, n)
    promotion = rng.binomial(1, 0.3, n)
    season = rng.choice(["low", "medium", "high"], n, p=[0.3, 0.4, 0.3])

    season_effect = np.select(
        [season == "medium", season == "high"],
        [0.25, 0.55],
        default=0.0,
    )

    # Synthetic purchase probabilities for pipeline testing only.
    log_odds = (
        -2.0
        + 5.0 * discount
        - 0.002 * price
        + 0.8 * promotion
        + 0.8 * (competitor_price / price - 1)
        + season_effect
    )
    probability = 1 / (1 + np.exp(-log_odds))
    purchase = rng.binomial(1, probability)

    return pd.DataFrame({
        "customer_id": np.arange(1, n + 1),
        "price": price.round(2),
        "discount": discount.round(3),
        "competitor_price": competitor_price.round(2),
        "promotion": promotion,
        "season": season,
        "purchase": purchase,
    })


if __name__ == "__main__":
    project_root = Path(__file__).resolve().parent
    output_path = project_root / "data" / "pricing_data.csv"
    output_path.parent.mkdir(parents=True, exist_ok=True)

    df = generate_pricing_data()
    df.to_csv(output_path, index=False)

    print(f"Generated {len(df)} synthetic records.")
    print(f"Saved dataset to: {output_path}")
    print(f"Purchase rate: {df['purchase'].mean():.1%}")
    print(df.head().to_string(index=False))
