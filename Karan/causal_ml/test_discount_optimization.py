from pathlib import Path

import pandas as pd


def test_discount_optimization_report():
    root = Path(__file__).resolve().parents[2]
    report_path = root / "data" / "discount_optimization_report.csv"
    report = pd.read_csv(report_path)

    assert len(report) == 11

    metrics = report.set_index("metric")["value"]

    assert metrics["rows_evaluated"] == 500
    assert abs(
        metrics["original_total_discount_fraction"]
        - metrics["optimized_total_discount_fraction"]
    ) < 1e-6

    assert 0 <= metrics["optimized_mean_discount"] <= 0.35
    assert metrics["mean_absolute_discount_change"] >= 0
    assert metrics["rows_at_35_percent_cap"] <= 500


    print("All discount optimization report tests passed.")


if __name__ == "__main__":
    test_discount_optimization_report()