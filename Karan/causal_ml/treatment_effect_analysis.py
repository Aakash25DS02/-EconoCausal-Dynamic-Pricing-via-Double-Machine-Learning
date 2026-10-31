from pathlib import Path

import pandas as pd
from sklearn.model_selection import train_test_split
from econml.dml import LinearDML
from sklearn.ensemble import RandomForestRegressor, RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from effect_summary import summarize_effects
from sklearn.metrics import mean_squared_error, r2_score


def main():
    project_root = Path(__file__).resolve().parents[2]
    data_path = project_root / "data" / "pricing_data.csv"

    if not data_path.exists():
        raise FileNotFoundError(f"Dataset not found: {data_path}")

    df = pd.read_csv(data_path)

    required = [
        "discount",
        "price",
        "competitor_price",
        "promotion",
        "season",
        "purchase",
    ]
    df = df.dropna(subset=required).copy()

    # Treatment: discount level; outcome: purchase (0/1).
    # Adjust for other observed pricing and seasonal factors.
    X = pd.get_dummies(
        df[["price", "competitor_price", "promotion", "season"]],
        columns=["season"],
        drop_first=True,
        dtype=float,
    )
    T = df["discount"].astype(float)
    Y = df["purchase"].astype(float)

    X_train, X_test, T_train, T_test, Y_train, Y_test = train_test_split(
        X, T, Y, test_size=0.25, random_state=42
    )

    model = LinearDML(
        model_y=RandomForestRegressor(
            n_estimators=100, min_samples_leaf=10, random_state=42
        ),
        model_t=RandomForestRegressor(
            n_estimators=100, min_samples_leaf=10, random_state=42
        ),
        discrete_treatment=False,
        random_state=42,
    )

    model.fit(Y_train, T_train, X=X_train)

    outcome_model = RandomForestRegressor(
    n_estimators=100,
    min_samples_leaf=10,
    random_state=42,
    )
    prediction_X = pd.concat([X, T.rename("discount")], axis=1)

    prediction_X_train, prediction_X_test, prediction_Y_train, prediction_Y_test = train_test_split(
        prediction_X, Y, test_size=0.25, random_state=42
    )

    outcome_model = RandomForestRegressor(
        n_estimators=100,
        min_samples_leaf=10,
        random_state=42,
    )
    outcome_model.fit(prediction_X_train, prediction_Y_train)

    predicted_purchase = outcome_model.predict(prediction_X_test)
    rmse = mean_squared_error(prediction_Y_test, predicted_purchase) ** 0.5
    r2 = r2_score(prediction_Y_test, predicted_purchase)

    print("\n=== Outcome Prediction Evaluation ===")
    print(f"RMSE: {rmse:.4f}")
    print(f"R²:   {r2:.4f}")

    # Estimated change in purchase probability for a 10 percentage-point
    # increase in discount, at the observed feature values.

    effects = model.effect(X_test, T0=T_test, T1=T_test + 0.10)
    summarize_effects(effects)

    results = pd.DataFrame({
    "discount": T_test.to_numpy(),
    "estimated_effect": effects,
    })

    output_path = project_root / "data" / "treatment_effects.csv"
    results.to_csv(output_path, index=False)
    print(f"Individual treatment effects saved to: {output_path}")

    print(f"Rows used: {len(df)}")
    print(f"Test rows: {len(X_test)}")
    print(
        "Mean estimated effect of +10 percentage points discount "
        f"on purchase probability: {effects.mean():.4f}"
    )
    print(
        "This is a synthetic-data experiment, not evidence of real-world "
        "causal impact."
    )


if __name__ == "__main__":
    main()
