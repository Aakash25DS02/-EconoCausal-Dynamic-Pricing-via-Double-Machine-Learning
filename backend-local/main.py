
from pathlib import Path
import numpy as np
import pandas as pd
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
app = FastAPI(
    title="EconoCausal API",
    description="Backend for causal discount analysis and budget-aware pricing.",
    version="0.1.0",
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:5174",
        "http://127.0.0.1:5174",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Find the dataset in the existing project folder structure.
PROJECT_DIR = Path(__file__).resolve().parent

DATA_CANDIDATES = [
    PROJECT_DIR / "data" / "pricing_data.csv",
    PROJECT_DIR / "pricing_data.csv",
    PROJECT_DIR.parent / "data" / "pricing_data.csv",
    PROJECT_DIR.parent / "backend" / "data" / "pricing_data.csv",
    PROJECT_DIR.parent.parent / "data" / "pricing_data.csv",
    PROJECT_DIR.parent.parent / "backend" / "data" / "pricing_data.csv",
]

DATA_PATH = next(
    (path for path in DATA_CANDIDATES if path.exists()),
    PROJECT_DIR / "data" / "pricing_data.csv",
)

REQUIRED_COLUMNS = [
    "price",
    "discount",
    "purchase",
]


def load_dataset() -> pd.DataFrame:
    if not DATA_PATH.exists():
        raise HTTPException(
            status_code=404,
            detail=(
                "Dataset not found. Run generate_data.py "
                "and ensure pricing_data.csv is in the project data folder."
            ),
        )

    try:
        df = pd.read_csv(DATA_PATH)
    except (OSError, pd.errors.ParserError) as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Could not read the pricing dataset: {exc}",
        ) from exc

    missing_columns = [
        column for column in REQUIRED_COLUMNS
        if column not in df.columns
    ]

    if missing_columns:
        raise HTTPException(
            status_code=422,
            detail=f"Missing required columns: {missing_columns}",
        )

    if df.empty:
        raise HTTPException(
            status_code=422,
            detail="The pricing dataset contains no records.",
        )

    if df[REQUIRED_COLUMNS].isnull().any().any():
        raise HTTPException(
            status_code=422,
            detail="Required columns contain missing values.",
        )

    return df


@app.get("/")
def root():
    return {
        "project": "EconoCausal",
        "message": "Dynamic pricing and causal analysis API",
        "version": "0.1.0",
        "docs": "/docs",
    }


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/data/summary")
def data_summary():
    df = load_dataset()

    return {
        "dataset_path": str(DATA_PATH),
        "rows": len(df),
        "columns": list(df.columns),
        "missing_values": {
            column: int(count)
            for column, count in df.isnull().sum().items()
        },
        "purchase_rate": round(float(df["purchase"].mean()), 4),
        "average_discount": round(float(df["discount"].mean()), 4),
        "average_price": round(float(df["price"].mean()), 2),
        "discount_range": [
            float(df["discount"].min()),
            float(df["discount"].max()),
        ],
    }

@app.get("/analysis/promotion-effect")
def promotion_effect():
    df = load_dataset().copy()

    required = [
        "promotion",
        "purchase",
        "price",
        "discount",
        "competitor_price",
        "season",
    ]

    missing = [col for col in required if col not in df.columns]
    if missing:
        raise HTTPException(
            status_code=422,
            detail=f"Missing analysis columns: {missing}",
        )

    # Prepare variables and remove incomplete records.
    df = df[required].dropna()

    if df.empty:
        raise HTTPException(
            status_code=422,
            detail="No complete records available for analysis.",
        )

    # Convert categorical season into indicator variables.
    season_dummies = pd.get_dummies(
        df["season"].astype(str),
        prefix="season",
        drop_first=True,
        dtype=float,
    )

    numeric = df[
        [
            "promotion",
            "purchase",
            "price",
            "discount",
            "competitor_price",
        ]
    ].apply(pd.to_numeric, errors="coerce")

    analysis = pd.concat([numeric, season_dummies], axis=1).dropna()

    if analysis.empty:
        raise HTTPException(
            status_code=422,
            detail="No valid numeric records available.",
        )

    if analysis["promotion"].nunique() < 2:
        raise HTTPException(
            status_code=422,
            detail="Both promotion groups are required.",
        )

    y = analysis["purchase"].to_numpy(dtype=float)

    if not np.isin(y, [0, 1]).all():
        raise HTTPException(
            status_code=422,
            detail="Purchase must contain only 0 and 1.",
        )

    feature_names = [
        col for col in analysis.columns
        if col != "purchase"
    ]

    X = np.column_stack([
        np.ones(len(analysis)),
        analysis[feature_names].to_numpy(dtype=float),
    ])

    # OLS linear probability model.
    xtx_inverse = np.linalg.pinv(X.T @ X)
    coefficients = xtx_inverse @ X.T @ y
    residuals = y - X @ coefficients

    n, k = X.shape

    if n <= k:
        raise HTTPException(
            status_code=422,
            detail="Not enough observations for the adjusted model.",
        )

    # HC1 heteroskedasticity-robust covariance estimate.
    meat = X.T @ (
        X * (residuals ** 2)[:, None]
    )
    covariance = (
        (n / (n - k))
        * xtx_inverse
        @ meat
        @ xtx_inverse
    )

    promotion_index = feature_names.index("promotion") + 1
    effect = float(coefficients[promotion_index])
    standard_error = float(
        np.sqrt(max(covariance[promotion_index, promotion_index], 0))
    )

    # Approximate 95% confidence interval.
    lower = effect - 1.96 * standard_error
    upper = effect + 1.96 * standard_error

    treated = analysis.loc[
        analysis["promotion"] == 1, "purchase"
    ]
    control = analysis.loc[
        analysis["promotion"] == 0, "purchase"
    ]

    return {
        "analysis_type": "adjusted_linear_probability_model",
        "dataset_type": "synthetic",
        "outcome": "purchase",
        "treatment": "promotion",
        "observations": int(n),
        "promotion_count": int(len(treated)),
        "control_count": int(len(control)),
        "promotion_purchase_rate": round(float(treated.mean()), 4),
        "control_purchase_rate": round(float(control.mean()), 4),
        "adjusted_effect": round(effect, 4),
        "adjusted_effect_percentage_points": round(effect * 100, 2),
        "robust_standard_error": round(standard_error, 4),
        "confidence_interval_95": [
            round(lower, 4),
            round(upper, 4),
        ],
        "covariates": feature_names[1:],
        "causal_warning": (
            "Synthetic observational data. The adjusted estimate is not "
            "proof of causation; unmeasured confounding may remain."
        ),
    }


@app.get("/analysis/promotion-effect-dml")
def promotion_effect_dml():
    from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
    from sklearn.model_selection import StratifiedKFold

    df = load_dataset().copy()

    required = [
        "promotion",
        "purchase",
        "price",
        "discount",
        "competitor_price",
        "season",
    ]

    missing = [col for col in required if col not in df.columns]
    if missing:
        raise HTTPException(
            status_code=422,
            detail=f"Missing analysis columns: {missing}",
        )

    df = df[required].dropna().copy()

    numeric_cols = [
        "promotion", "purchase", "price",
        "discount", "competitor_price",
    ]
    df[numeric_cols] = df[numeric_cols].apply(
        pd.to_numeric, errors="coerce"
    )
    df = df.dropna()

    if df.empty or df["promotion"].nunique() != 2:
        raise HTTPException(
            status_code=422,
            detail="Valid records from both promotion groups are required.",
        )

    if not df["purchase"].isin([0, 1]).all():
        raise HTTPException(
            status_code=422,
            detail="Purchase must contain only 0 and 1.",
        )

    y = df["purchase"].to_numpy(dtype=float)
    treatment = df["promotion"].to_numpy(dtype=int)

    X_df = pd.concat(
        [
            df[["price", "discount", "competitor_price"]].reset_index(drop=True),
            pd.get_dummies(
                df["season"].astype(str),
                prefix="season",
                drop_first=True,
                dtype=float,
            ).reset_index(drop=True),
        ],
        axis=1,
    )
    X = X_df.to_numpy(dtype=float)

    counts = np.bincount(treatment, minlength=2)
    folds = min(5, int(counts.min()))

    if folds < 2:
        raise HTTPException(
            status_code=422,
            detail="At least two records per treatment group are required.",
        )

    n = len(y)
    m1 = np.zeros(n)
    m0 = np.zeros(n)
    propensity = np.zeros(n)

    splitter = StratifiedKFold(
        n_splits=folds, shuffle=True, random_state=42
    )

    for train_idx, test_idx in splitter.split(X, treatment):
        X_train, X_test = X[train_idx], X[test_idx]
        t_train = treatment[train_idx]
        y_train = y[train_idx]

        # Estimate the probability of receiving a promotion.
        treatment_model = RandomForestClassifier(
            n_estimators=200,
            min_samples_leaf=10,
            random_state=42,
            n_jobs=-1,
        )
        treatment_model.fit(X_train, t_train)
        propensity[test_idx] = treatment_model.predict_proba(
            X_test
        )[:, 1]

        # Estimate outcomes separately for promoted and control groups.
        for group, predictions in [(1, m1), (0, m0)]:
            group_mask = t_train == group

            if group_mask.sum() < 2:
                raise HTTPException(
                    status_code=422,
                    detail="Insufficient records in a training treatment group.",
                )

            outcome_model = RandomForestRegressor(
                n_estimators=200,
                min_samples_leaf=10,
                random_state=42,
                n_jobs=-1,
            )
            outcome_model.fit(
                X_train[group_mask], y_train[group_mask]
            )
            predictions[test_idx] = outcome_model.predict(X_test)

    # Clip extreme propensity estimates for numerical stability.
    propensity = np.clip(propensity, 0.05, 0.95)

    # Cross-fitted doubly robust / orthogonal score for the ATE.
    scores = (
        m1 - m0
        + treatment * (y - m1) / propensity
        - (1 - treatment) * (y - m0) / (1 - propensity)
    )

    effect = float(np.mean(scores))
    standard_error = float(
        np.std(scores, ddof=1) / np.sqrt(n)
    )

    lower = effect - 1.96 * standard_error
    upper = effect + 1.96 * standard_error

    treated = y[treatment == 1]
    control = y[treatment == 0]

    return {
        "analysis_type": "cross_fitted_doubly_robust_dml",
        "dataset_type": "synthetic",
        "outcome": "purchase",
        "treatment": "promotion",
        "observations": int(n),
        "cross_fitting_folds": int(folds),
        "promotion_count": int(len(treated)),
        "control_count": int(len(control)),
        "promotion_purchase_rate": round(float(treated.mean()), 4),
        "control_purchase_rate": round(float(control.mean()), 4),
        "dml_effect": round(effect, 4),
        "dml_effect_percentage_points": round(effect * 100, 2),
        "standard_error": round(standard_error, 4),
        "confidence_interval_95": [
            round(lower, 4), round(upper, 4)
        ],
        "covariates": list(X_df.columns),
        "causal_warning": (
            "Synthetic data. Cross-fitting and orthogonal scores do not "
            "eliminate bias from unmeasured confounding or model limitations."
        ),
    }


@app.get("/data/preview")
def data_preview():
    df = load_dataset()
    return {
        "records": df.head(10).to_dict(orient="records")
    }


from pydantic import BaseModel, Field
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder
from sklearn.pipeline import Pipeline
from sklearn.linear_model import LogisticRegression
import heapq


class AllocationRequest(BaseModel):
    budget: float = Field(gt=0)


@app.post("/allocation/optimize")
def optimize_budget_allocation(request: AllocationRequest):
    try:
        df = load_dataset()

        required = [
            "customer_id",
            "price",
            "discount",
            "competitor_price",
            "promotion",
            "season",
            "purchase",
        ]

        missing = [column for column in required if column not in df.columns]
        if missing:
            raise HTTPException(
                status_code=400,
                detail=f"Dataset is missing columns: {missing}",
            )

        # Prepare the historical dataset.
        data = df[required].dropna().copy()

        if data.empty or data["purchase"].nunique() < 2:
            raise HTTPException(
                status_code=400,
                detail="The dataset must contain both purchase outcomes (0 and 1).",
            )

        numeric_features = [
            "price",
            "competitor_price",
            "promotion",
            "discount",
        ]

        preprocessor = ColumnTransformer(
            transformers=[
                ("numeric", "passthrough", numeric_features),
                ("season", OneHotEncoder(handle_unknown="ignore"), ["season"]),
            ]
        )

        model = Pipeline(
            steps=[
                ("preprocessor", preprocessor),
                ("classifier", LogisticRegression(max_iter=1000)),
            ]
        )

        features = data[numeric_features + ["season"]]
        target = data["purchase"].astype(int)

        model.fit(features, target)

        # Evaluate discount choices from 0% to 35%.
        discount_levels = np.round(np.arange(0, 0.351, 0.01), 2)

        customer_count = len(data)
        discount_count = len(discount_levels)

        candidate_rows = data.loc[
            data.index.repeat(discount_count)
        ].copy()

        candidate_rows["discount"] = np.tile(
            discount_levels, customer_count
        )

        candidate_features = candidate_rows[
            numeric_features + ["season"]
        ]

        probabilities = model.predict_proba(candidate_features)[:, 1]
        probability_matrix = probabilities.reshape(
            customer_count, discount_count
        )

        prices = data["price"].to_numpy()

        # Expected purchases and expected discount expenditure.
        expected_spend = (
            probability_matrix
            * prices[:, None]
            * discount_levels[None, :]
        )

        # Begin with a 0% discount for every customer.
        chosen_levels = np.zeros(customer_count, dtype=int)
        remaining_budget = float(request.budget)

        # Greedy allocation: choose the next discount increase
        # with the highest predicted purchase improvement per rupee.
        allocation_heap = []

        def add_next_option(customer_index):
            current_level = chosen_levels[customer_index]
            next_level = current_level + 1

            if next_level >= discount_count:
                return

            purchase_gain = (
                probability_matrix[customer_index, next_level]
                - probability_matrix[customer_index, current_level]
            )

            spend_increase = (
                expected_spend[customer_index, next_level]
                - expected_spend[customer_index, current_level]
            )

            if purchase_gain > 0 and spend_increase > 0:
                ratio = purchase_gain / spend_increase
                heapq.heappush(
                    allocation_heap,
                    (-ratio, customer_index, next_level, spend_increase),
                )

        for customer_index in range(customer_count):
            add_next_option(customer_index)

        while allocation_heap:
            _, customer_index, next_level, spend_increase = (
                heapq.heappop(allocation_heap)
            )

            if spend_increase > remaining_budget:
                continue

            chosen_levels[customer_index] = next_level
            remaining_budget -= spend_increase

            add_next_option(customer_index)

        selected_rows = np.arange(customer_count)
        selected_probabilities = probability_matrix[
            selected_rows, chosen_levels
        ]
        selected_spend = expected_spend[
            selected_rows, chosen_levels
        ]

        baseline_purchases = float(
            probability_matrix[:, 0].sum()
        )
        recommended_purchases = float(
            selected_probabilities.sum()
        )
        total_expected_spend = float(selected_spend.sum())

        allocation = []

        for index, (_, customer) in enumerate(data.iterrows()):
            allocation.append({
                "customer_id": int(customer["customer_id"]),
                "price": round(float(prices[index]), 2),
                "recommended_discount": round(
                    float(discount_levels[chosen_levels[index]]), 2
                ),
                "predicted_purchase_probability": round(
                    float(selected_probabilities[index]), 4
                ),
                "expected_discount_spend": round(
                    float(selected_spend[index]), 2
                ),
            })

        allocation.sort(
            key=lambda item: item["recommended_discount"],
            reverse=True,
        )

        return {
            "status": "success",
            "method": "Greedy budget allocation heuristic",
            "budget": round(float(request.budget), 2),
            "expected_discount_spend": round(total_expected_spend, 2),
            "remaining_budget": round(
                max(0.0, float(request.budget) - total_expected_spend), 2
            ),
            "budget_utilization_percent": round(
                (total_expected_spend / float(request.budget)) * 100, 2
            ),
            "baseline_expected_purchases": round(baseline_purchases, 2),
            "recommended_expected_purchases": round(
                recommended_purchases, 2
            ),
            "expected_purchase_improvement": round(
                recommended_purchases - baseline_purchases, 2
            ),
            "customer_count": customer_count,
            "allocations": allocation,
            "note": (
                "Predictions are based on the available dataset. "
                "Expected discount spend assumes a discount is incurred "
                "only when a customer makes a purchase. This is an "
                "illustrative model-based estimate, not a causal or "
                "profit guarantee. The greedy method is a heuristic."
            ),
        }

    except HTTPException:
        raise
    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=f"Allocation failed: {str(error)}",
        )
