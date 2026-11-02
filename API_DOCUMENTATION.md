# EconoCausal API Documentation

## 1. Project Overview

EconoCausal is a dynamic pricing and causal analysis project that explores customer purchasing behavior and discount recommendations.

The backend is built using FastAPI and Python. It provides endpoints to check API health, inspect pricing data, summarize dataset statistics, and obtain a recommended discount.

**Important:** The current discount optimizer uses predictive scenario comparisons. Its recommendation should not be treated as a proven causal effect or a guarantee of increased profit.

## 2. Technologies Used

- Python
- FastAPI
- Pandas
- NumPy
- Uvicorn
- CSV dataset

## 3. Project Setup

Open a terminal in the project root directory.

Install the required dependencies using the project's requirements file:

```cmd
python -m pip install -r backend\requirements.txt
```

Ensure the pricing dataset `data/pricing_data.csv` is available in the expected project data folder.

## 4. Start the API

From the project root directory, run:

```cmd
python -m uvicorn app.main:app --reload
```

By default, the API is available at:

`http://127.0.0.1:8000`

To open the interactive API documentation, visit:

`http://127.0.0.1:8000/docs`

To view the OpenAPI schema, visit:

`http://127.0.0.1:8000/openapi.json`

Keep the terminal running while using the API.

## 5. API Endpoints

### GET /

Returns basic project information and the API documentation path.

Example response:

```json
{
  "project": "EconoCausal",
  "message": "Dynamic pricing and causal analysis API",
  "version": "0.2.0",
  "docs": "/docs"
}
```

### GET /health

Checks whether the API is running.

Example response:

```json
{
  "status": "ok"
}
```

### GET /data/summary

Returns a summary of the pricing dataset, including:

- Number of rows
- Dataset column names
- Missing-value counts
- Purchase rate
- Average discount
- Average price
- Minimum and maximum observed discounts

Example response structure:

```json
{
  "dataset_path": "path/to/pricing_data.csv",
  "rows": 2000,
  "columns": [
    "customer_id",
    "price",
    "discount",
    "competitor_price",
    "promotion",
    "season",
    "purchase"
  ],
  "missing_values": {},
  "purchase_rate": 0.176,
  "average_discount": 0.1726,
  "average_price": 552.55,
  "discount_range": [0.0, 0.35]
}
```

The example values describe the project's current synthetic dataset and may change if the data changes.

### GET /data/preview

Returns the first 10 records from the pricing dataset.

The response contains a `records` field with a list of records. Each record includes the available dataset columns.

### GET /discount/recommendation

Evaluates discount scenarios and returns the recommended discount and related prediction metrics.

The response includes fields such as:

- `recommended_discount`
- `predicted_purchase_probability`
- `estimated_revenue_per_record`
- `observations`
- `scenarios_evaluated`
- `all_scenarios`

The current optimizer evaluates 36 discount scenarios, from 0.00 to 0.35 in increments of 0.01.

The estimated revenue per record is a revenue proxy, not profit. The recommendation is based on model predictions and does not establish that a discount will cause the predicted outcome in real-world use.

## 6. Error Handling

The API uses HTTP status codes to communicate errors.

- `404 Not Found`: The dataset or requested endpoint does not exist.
- `422 Unprocessable Entity`: The dataset is empty, required columns are missing, required values are missing, or the recommendation input is invalid.
- `500 Internal Server Error`: The dataset cannot be read due to a file or parsing error.

The exact response depends on the endpoint and the error encountered.

## 7. Automated Tests

Run the project's DML model and API tests from the project root:

```cmd
python -m unittest test_dml_model.py test_api.py -v
```

The tests cover the DML model, API health, dataset summary, dataset preview, discount recommendation, and unknown endpoint handling.

## 8. Limitations

- The dataset is synthetic and may not represent actual customer behavior.
- Predictive relationships do not automatically establish causality.
- Causal interpretations require suitable identification assumptions and validation.
- The revenue estimate does not account for costs, margins, or other business constraints.
- Model predictions and discount recommendations should be validated before real-world deployment.

## 9. Future Improvements

- Add more comprehensive model validation.
- Evaluate recommendations using appropriate causal inference methods.
- Incorporate product costs and profit-based optimization.
- Add input schemas and stronger response validation.
- Expand automated tests for invalid and missing data.
