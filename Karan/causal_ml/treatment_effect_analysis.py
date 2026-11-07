from pathlib import Path

import pandas as pd
from sklearn.model_selection import train_test_split
from econml.dml import LinearDML
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error, r2_score

from effect_summary import summarize_effects


def main():
    # Locate dataset
    project_root = Path(__file__).resolve().parents[2]
    data_path = project_root / "data" / "pricing_data.csv"

    if not data_path.exists():
        raise FileNotFoundError(f"Dataset not found: {data_path}")

    df = pd.read_csv(data_path)

    required = [
        "customer_id",
        "discount",
        "price",
        "competitor_price",
        "promotion",
        "season",
        "purchase",
    ]

    missing = sorted(set(required) - set(df.columns))
    if missing:
        raise ValueError(f"Missing columns: {missing}")

    df = df.dropna(subset=required).copy()

    if df.empty:
        raise ValueError("Dataset is empty after removing missing values.")

    if not df["discount"].between(0, 0.35).all():
        raise ValueError("Discount must be between 0 and 0.35.")

    if not df["purchase"].isin([0, 1]).all():
        raise ValueError("Purchase must contain only 0 and 1.")

    # Prepare customer features
    X = pd.get_dummies(
        df[["price", "competitor_price", "promotion", "season"]],
        columns=["season"],
        drop_first=True,
        dtype=float,
    )

    T = df["discount"].astype(float)
    Y = df["purchase"].astype(float)
    customer_ids = df["customer_id"]

    # Train-test split
    (
        X_train,
        X_test,
        T_train,
        T_test,
        Y_train,
        Y_test,
        id_train,
        id_test,
    ) = train_test_split(
        X,
        T,
        Y,
        customer_ids,
        test_size=0.25,
        random_state=42,
    )

    # Train LinearDML model
    model = LinearDML(
        model_y=RandomForestRegressor(
            n_estimators=100,
            min_samples_leaf=10,
            random_state=42,
        ),
        model_t=RandomForestRegressor(
            n_estimators=100,
            min_samples_leaf=10,
            random_state=42,
        ),
        discrete_treatment=False,
        random_state=42,
    )

    model.fit(Y_train, T_train, X=X_train)

    # Evaluate outcome prediction separately
    prediction_X = pd.concat(
        [X, T.rename("discount")],
        axis=1,
    )

    (
        prediction_X_train,
        prediction_X_test,
        prediction_Y_train,
        prediction_Y_test,
    ) = train_test_split(
        prediction_X,
        Y,
        test_size=0.25,
        random_state=42,
    )

    outcome_model = RandomForestRegressor(
        n_estimators=100,
        min_samples_leaf=10,
        random_state=42,
    )

    outcome_model.fit(prediction_X_train, prediction_Y_train)

    predicted_purchase = outcome_model.predict(prediction_X_test)

    rmse = mean_squared_error(
        prediction_Y_test,
        predicted_purchase,
    ) ** 0.5

    r2 = r2_score(
        prediction_Y_test,
        predicted_purchase,
    )

    print("\n========== OUTCOME PREDICTION ==========")
    print(f"RMSE: {rmse:.4f}")
    print(f"R2:   {r2:.4f}")

    # Standardized treatment comparison:
    # 0% discount versus 10% discount
    reference_discount = 0.0
    target_discount = 0.10

    effects = model.effect(
        X_test,
        T0=reference_discount,
        T1=target_discount,
    )

    summarize_effects(effects)

    # Save individual treatment effects
    results = pd.DataFrame({
        "customer_id": id_test.to_numpy(),
        "observed_discount": T_test.to_numpy(),
        "reference_discount": reference_discount,
        "target_discount": target_discount,
        "estimated_effect": effects,
    })

    output_path = project_root / "data" / "treatment_effects.csv"
    results.to_csv(output_path, index=False)

    print("\n========== TREATMENT EFFECT ANALYSIS ==========")
    print(f"Rows used       : {len(df)}")
    print(f"Training rows   : {len(X_train)}")
    print(f"Testing rows    : {len(X_test)}")
    print("Comparison      : 0% discount vs 10% discount")
    print(f"Mean effect     : {effects.mean():.4f}")
    print(f"Saved results   : {output_path}")

    print(
        "\nNote: This is an exploratory synthetic-data experiment, "
        "not evidence of real-world causal impact."
    )


if __name__ == "__main__":
    main()