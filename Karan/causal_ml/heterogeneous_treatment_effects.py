
from pathlib import Path

import pandas as pd
from sklearn.model_selection import train_test_split

from causal_service import CausalPricingService


def create_price_segments(series):
    ranked = series.rank(method="first")

    return pd.qcut(
        ranked,
        q=3,
        labels=["Low", "Medium", "High"]
    )


def main():
    project_root = Path(__file__).resolve().parents[2]
    data_path = project_root / "data" / "pricing_data.csv"

    if not data_path.exists():
        raise FileNotFoundError(f"Dataset not found: {data_path}")

    df = pd.read_csv(data_path)

    print("Original dataset:", df.shape)

    # Split customers into training and testing sets.
    train_df, test_df = train_test_split(
        df,
        test_size=0.20,
        random_state=42
    )

    print("Training customers:", len(train_df))
    print("Testing customers:", len(test_df))

    # Train the existing causal service.
    service = CausalPricingService(random_state=42)
    service.fit(train_df)

    print("\nLinearDML model trained successfully.")

    # Estimate effects only on unseen test customers.
    results = service.estimate_ite(
        test_df,
        reference_discount=0.0,
        target_discount=0.10
    )

    analysis = test_df.merge(
        results[["customer_id", "estimated_effect"]],
        on="customer_id",
        how="inner",
        validate="one_to_one"
    )

    # Create numerical feature segments.
    analysis["price_segment"] = create_price_segments(
        analysis["price"]
    )

    analysis["competitor_price_segment"] = create_price_segments(
        analysis["competitor_price"]
    )

    segment_columns = {
        "Season": "season",
        "Promotion": "promotion",
        "Price": "price_segment",
        "Competitor Price": "competitor_price_segment"
    }

    summaries = []

    for segment_type, column in segment_columns.items():

        summary = (
            analysis.groupby(column, observed=True)
            ["estimated_effect"]
            .agg(
                customer_count="count",
                mean_effect="mean",
                median_effect="median",
                std_effect="std"
            )
            .reset_index()
            .rename(columns={column: "segment"})
        )

        positive_counts = (
            analysis.assign(
                positive=analysis["estimated_effect"] > 0
            )
            .groupby(column, observed=True)["positive"]
            .sum()
            .reset_index(name="positive_effect_customers")
        )

        summary = summary.merge(
            positive_counts,
            left_on="segment",
            right_on=column,
            how="left"
        )

        summary["positive_effect_percentage"] = (
            summary["positive_effect_customers"]
            / summary["customer_count"] * 100
        )

        summary["segment_type"] = segment_type

        summaries.append(
            summary.drop(columns=[column])
        )

    final_summary = pd.concat(
        summaries,
        ignore_index=True
    )

    # Save test-customer estimates and segment summary.
    customer_output = (
        project_root / "data" / "heterogeneous_treatment_effects.csv"
    )

    summary_output = (
        project_root / "data" / "hte_segment_summary.csv"
    )

    analysis.to_csv(customer_output, index=False)
    final_summary.to_csv(summary_output, index=False)

    print("\n========== HTE SEGMENT ANALYSIS ==========")

    for segment_type in segment_columns:

        print(f"\n--- {segment_type} ---")

        print(
            final_summary[
                final_summary["segment_type"] == segment_type
            ][
                [
                    "segment",
                    "customer_count",
                    "mean_effect",
                    "positive_effect_percentage"
                ]
            ].to_string(index=False)
        )

    print("\n========== OVERALL RESULTS ==========")

    print("Test customers analysed:", len(analysis))
    print(
        "Average estimated effect:",
        round(analysis["estimated_effect"].mean(), 4)
    )

    print("\nSaved files:")
    print(customer_output)
    print(summary_output)

    print(
        "\nNote: These are exploratory estimates from synthetic data. "
        "They do not establish real-world causal impact."
    )


if __name__ == "__main__":
    main()
