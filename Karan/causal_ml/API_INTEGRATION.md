# Karan – Causal ML API Integration Contract

Owner: Member 2 – Causal Machine Learning
Consumer: Member 1 – Backend Integration

## 1. Available components

- causal_service.py: EconML LinearDML training and customer-level ITE estimation.
- data_drift_detector.py: PSI and statistical drift checks.
- effect_summary.py: Treatment-effect summaries.
- dowhy_causal_dag.py: Causal graph.
- dowhy_refutation_tests.py: DoWhy refutation tests.

## 2. Model initialization

The backend should load the historical pricing dataset and train the
causal service once during application startup.

Suggested integration:

    from Karan.causal_ml.causal_service import CausalPricingService
    import pandas as pd

    reference_data = pd.read_csv("data/pricing_data.csv")

    causal_service = CausalPricingService()
    causal_service.fit(reference_data)

Do not retrain the model for every API request.

## 3. Proposed endpoint: POST /causal/estimate

This is a proposed route. The backend owner decides the final route name.

Request fields:

- customers: list of customer records.
- reference_discount: starting discount, default 0.0.
- target_discount: comparison discount, default 0.10.

Each customer requires:

- customer_id
- price
- competitor_price
- promotion
- season

The inference request does not require purchase or historical discount.
Those are required for model training, not for estimating effects
for new customers.

Example request:

    {
      "reference_discount": 0.0,
      "target_discount": 0.10,
      "customers": [
        {
          "customer_id": "C1001",
          "price": 100.0,
          "competitor_price": 95.0,
          "promotion": 1,
          "season": "high"
        }
      ]
    }

Backend function:

    results = causal_service.estimate_ite(
        pd.DataFrame(request["customers"]),
        reference_discount=request.get("reference_discount", 0.0),
        target_discount=request.get("target_discount", 0.10)
    )

    summary = causal_service.summarize(results)

Expected response structure:

    {
      "customer_count": 1,
      "reference_discount": 0.0,
      "target_discount": 0.10,
      "results": [
        {
          "customer_id": "C1001",
          "estimated_effect": 0.05
        }
      ],
      "summary": {
        "customer_count": 1,
        "mean_effect": 0.05
      }
    }

The numeric effect above is illustrative, not an actual model result.

## 4. Proposed endpoint: POST /causal/drift

This is also a proposed route.

Use detect_data_drift() to compare a reference dataset against
a current observed dataset.

Suggested integration:

    from Karan.causal_ml.data_drift_detector import detect_data_drift

    report = detect_data_drift(reference_data, current_data)

The response includes:

- status
- reference_rows
- current_rows
- drifted_features
- warning_features
- per-feature PSI
- statistical p-values

PSI interpretation:

- Below 0.10: Stable
- 0.10 to below 0.20: Warning
- 0.20 or above: Drift detected

IMPORTANT:
The current drift detector requires all six monitored columns,
including purchase. Therefore, use it on observed batches after
purchase outcomes are available. It is not yet a feature-only
pre-purchase drift detector.

## 5. Model interpretation

estimated_effect represents the estimated change in purchase
probability for the specified discount comparison.

For example, 0.05 represents an estimated increase of five
percentage points in purchase probability.

It is not an actual purchase guarantee or a profit estimate.

The optimizer must separately calculate monetary costs and
revenue/profit implications.

## 6. Integration requirements

- Preserve customer_id throughout the API response.
- Validate incoming customer data.
- Reject missing IDs and duplicate customer IDs.
- Keep reference and target discount values within 0 to 0.35.
- Return JSON-compatible numeric values.
- Do not expose NaN or infinite estimates.
- Do not silently replace failed causal estimates with zero.
- Report drift warnings separately from causal estimates.
- Keep the trained reference model available for repeated requests.

## 7. Suggested error handling

- Invalid request or missing fields: HTTP 400.
- Model not initialized: HTTP 503.
- Invalid or non-finite model output: controlled HTTP 500 response.
- Drift detected: return the drift report; this is not an API failure.

## 8. Tests

Run the causal service tests:

    python -m pytest Karan/causal_ml/test_causal_service.py -v

Run the drift detector tests:

    python -m pytest Karan/causal_ml/test_data_drift_detector.py -v

Expected current result: 12 tests passed across both test files.

## 9. Ownership boundary

Member 2 owns causal inference, treatment-effect estimation,
causal validation and the drift detection component developed here.

Member 1 owns the final FastAPI application and endpoint integration.

Member 4 owns the optimization solver and final discount allocation.

Member 3 owns the React dashboard and visualization.

This document defines the integration contract; it does not create
or replace the main FastAPI application.
