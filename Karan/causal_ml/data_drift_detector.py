"""Monitor changes in customer pricing and purchasing data."""

import argparse
import json

import numpy as np
import pandas as pd
from scipy.stats import chi2_contingency, ks_2samp


NUMERIC_FEATURES = ["price", "discount", "competitor_price"]
CATEGORICAL_FEATURES = ["promotion", "season", "purchase"]

MONITORED_FEATURES = NUMERIC_FEATURES + CATEGORICAL_FEATURES

DEFAULT_PSI_THRESHOLD = 0.20
WARNING_PSI_THRESHOLD = 0.10
DEFAULT_P_VALUE_THRESHOLD = 0.05


def validate_drift_inputs(reference, current):
    """Validate both datasets before comparing distributions."""
    for name, df in [("Reference", reference), ("Current", current)]:
        if not isinstance(df, pd.DataFrame):
            raise TypeError(f"{name} data must be a pandas DataFrame.")

        if df.empty:
            raise ValueError(f"{name} dataset is empty.")

        missing = set(MONITORED_FEATURES) - set(df.columns)
        if missing:
            raise ValueError(
                f"{name} dataset is missing columns: {sorted(missing)}"
            )

        if df[MONITORED_FEATURES].isna().any().any():
            raise ValueError(
                f"{name} dataset contains missing monitored values."
            )

        for column in NUMERIC_FEATURES:
            values = pd.to_numeric(df[column], errors="coerce")
            if not np.isfinite(values.to_numpy(dtype=float)).all():
                raise ValueError(
                    f"{name} dataset has invalid values in {column}."
                )


def calculate_psi(reference_values, current_values, bins=10):
    """Calculate PSI using bins determined from reference data."""
    reference_values = np.asarray(reference_values, dtype=float)
    current_values = np.asarray(current_values, dtype=float)

    quantiles = np.quantile(
        reference_values, np.linspace(0, 1, bins + 1)
    )

    internal_edges = np.unique(quantiles[1:-1])
    edges = np.concatenate(([-np.inf], internal_edges, [np.inf]))

    # Handle constant reference features so new values can be detected.
    if reference_values.min() == reference_values.max():
        edges = np.array([
            -np.inf,
            reference_values[0],
            np.inf,
        ])

    reference_counts, _ = np.histogram(reference_values, bins=edges)
    current_counts, _ = np.histogram(current_values, bins=edges)

    epsilon = 1e-6

    reference_pct = np.maximum(
        reference_counts / len(reference_values), epsilon
    )
    current_pct = np.maximum(
        current_counts / len(current_values), epsilon
    )

    reference_pct /= reference_pct.sum()
    current_pct /= current_pct.sum()

    psi = np.sum(
        (current_pct - reference_pct)
        * np.log(current_pct / reference_pct)
    )

    return float(psi)


def calculate_categorical_psi(reference_values, current_values):
    """Calculate PSI for categorical and binary features."""
    reference_values = pd.Series(reference_values).astype(str)
    current_values = pd.Series(current_values).astype(str)

    categories = sorted(
        set(reference_values.unique())
        | set(current_values.unique())
    )

    reference_counts = (
        reference_values.value_counts()
        .reindex(categories, fill_value=0)
        .to_numpy(dtype=float)
    )

    current_counts = (
        current_values.value_counts()
        .reindex(categories, fill_value=0)
        .to_numpy(dtype=float)
    )

    epsilon = 1e-6

    reference_pct = np.maximum(
        reference_counts / len(reference_values), epsilon
    )
    current_pct = np.maximum(
        current_counts / len(current_values), epsilon
    )

    reference_pct /= reference_pct.sum()
    current_pct /= current_pct.sum()

    psi = np.sum(
        (current_pct - reference_pct)
        * np.log(current_pct / reference_pct)
    )

    if len(categories) < 2:
        p_value = 1.0
    else:
        contingency = np.vstack([
            reference_counts,
            current_counts,
        ])
        _, p_value, _, _ = chi2_contingency(
            contingency, correction=False
        )

    return float(psi), float(p_value)


def detect_data_drift(
    reference,
    current,
    psi_threshold=DEFAULT_PSI_THRESHOLD,
    p_value_threshold=DEFAULT_P_VALUE_THRESHOLD,
):
    """
    Compare reference and current customer data.

    PSI >= 0.20 indicates significant distribution drift.
    PSI between 0.10 and 0.20 indicates a warning.
    Statistical p-values are reported as supporting evidence.
    """
    if not 0 < psi_threshold:
        raise ValueError("PSI threshold must be positive.")

    if not 0 < p_value_threshold < 1:
        raise ValueError("P-value threshold must be between 0 and 1.")

    validate_drift_inputs(reference, current)

    feature_results = []

    for feature in NUMERIC_FEATURES:
        ref = pd.to_numeric(reference[feature]).to_numpy(dtype=float)
        cur = pd.to_numeric(current[feature]).to_numpy(dtype=float)

        psi = calculate_psi(ref, cur)
        _, p_value = ks_2samp(ref, cur)

        feature_results.append({
            "feature": feature,
            "feature_type": "numeric",
            "psi": psi,
            "p_value": float(p_value),
            "statistically_significant": bool(
                p_value < p_value_threshold
            ),
        })

    for feature in CATEGORICAL_FEATURES:
        psi, p_value = calculate_categorical_psi(
            reference[feature],
            current[feature],
        )

        feature_results.append({
            "feature": feature,
            "feature_type": (
                "behavior_outcome" if feature == "purchase"
                else "categorical"
            ),
            "psi": psi,
            "p_value": p_value,
            "statistically_significant": bool(
                p_value < p_value_threshold
            ),
        })

    drifted_features = []
    warning_features = []

    for result in feature_results:
        psi = result["psi"]

        if psi >= psi_threshold:
            result["status"] = "DRIFT"
            drifted_features.append(result["feature"])
        elif psi >= WARNING_PSI_THRESHOLD:
            result["status"] = "WARNING"
            warning_features.append(result["feature"])
        else:
            result["status"] = "STABLE"

    return {
        "status": (
            "DRIFT_DETECTED" if drifted_features
            else "WARNING" if warning_features
            else "NO_SIGNIFICANT_DRIFT"
        ),
        "reference_rows": int(len(reference)),
        "current_rows": int(len(current)),
        "psi_threshold": float(psi_threshold),
        "p_value_threshold": float(p_value_threshold),
        "drifted_features": drifted_features,
        "warning_features": warning_features,
        "features": feature_results,
    }


def main():
    parser = argparse.ArgumentParser(
        description="Detect drift in EconoCausal pricing data."
    )
    parser.add_argument("--reference", required=True)
    parser.add_argument("--current", required=True)
    parser.add_argument(
        "--psi-threshold",
        type=float,
        default=DEFAULT_PSI_THRESHOLD,
    )
    parser.add_argument("--output")

    args = parser.parse_args()

    reference = pd.read_csv(args.reference)
    current = pd.read_csv(args.current)

    report = detect_data_drift(
        reference,
        current,
        psi_threshold=args.psi_threshold,
    )

    output = json.dumps(report, indent=4)
    print(output)

    if args.output:
        with open(args.output, "w", encoding="utf-8") as file:
            file.write(output + "\n")
        print(f"\nDrift report saved to: {args.output}")


if __name__ == "__main__":
    main()
