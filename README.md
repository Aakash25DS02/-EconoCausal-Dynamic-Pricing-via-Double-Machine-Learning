# EconoCausal: Dynamic Pricing via Double Machine Learning

## Project Overview

EconoCausal is a machine learning project that explores how discounts influence customer purchase behavior. It combines Double Machine Learning (DML)-style estimation, predictive modeling, causal analysis, and discount optimization to support data-driven pricing decisions.

## The Problem

Traditional predictive ML models identify customers likely to purchase, but they do not necessarily determine whether a marketing offer will change customer behavior. Businesses may waste money discounting purchases that would happen anyway or miss customers whose behavior could be influenced by an offer.

## The Solution

EconoCausal uses DML-style methods to estimate the relationship between discounts and purchase behavior. It also evaluates discount scenarios using predictive models and explores constrained discount allocation using treatment-effect estimates.

## Key Features

- Synthetic pricing dataset with 2,000 customer records.
- DML-style discount effect estimation.
- Predictive discount scenario comparison across 36 discount levels.
- FastAPI backend for accessing project functionality.
- Dataset summary and preview endpoints.
- Promotion-effect analysis using adjusted and DML-style methods.
- Budget-constrained discount allocation module.
- Automated tests for models, APIs, and data validation.
- Frontend dashboard for project interaction.

## Technology Stack

- Python
- Pandas and NumPy
- Scikit-learn
- FastAPI and Uvicorn
- SciPy
- JavaScript and React
- Git and GitHub

## Project Structure

```text
EconoCausal/
├── Frontend/
├── app/
│   └── main.py
├── backend-local/
│   ├── data/
│   ├── main.py
│   ├── requirements.txt
│   └── test_main.py
├── data/
├── Karan/
├── member_4_mahesh/
├── shared/
├── dml_model.py
├── discount_optimizer.py
├── generate_data.py
├── test_api.py
├── test_api_validation.py
├── test_discount_optimizer.py
├── test_dml_model.py
├── API_DOCUMENTATION.md
├── PROJECT_OVERVIEW.md
└── README.md
```

## Installation and Setup

### 1. Clone the Repository

```bash
git clone https://github.com/Aakash25DS02/-EconoCausal-Dynamic-Pricing-via-Double-Machine-Learning.git
```

### 2. Open the Project Directory

```bash
cd -EconoCausal-Dynamic-Pricing-via-Double-Machine-Learning
```

## Run the Original Backend

The original backend is located in the `app/` directory.

### Install Dependencies

```bash
python -m pip install fastapi uvicorn pandas numpy scikit-learn
```

### Start the Application

Run from the project root:

```bash
python -m uvicorn app.main:app --reload
```

### Original Backend API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| GET | `/` | Project information |
| GET | `/health` | API health check |
| GET | `/data/summary` | Dataset summary |
| GET | `/data/preview` | Dataset preview |
| GET | `/discount/recommendation` | Discount scenario recommendation |

## Run the Integrated Backend

The integrated backend is located in `backend-local/`.

### Install Dependencies

From the project root:

```bash
python -m pip install -r backend-local/requirements.txt
```

### Start the Application

Run from the project root:

```bash
python -m uvicorn main:app --app-dir backend-local --reload
```

### Integrated Backend API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| GET | `/` | Project information |
| GET | `/health` | API health check |
| GET | `/data/summary` | Dataset summary |
| GET | `/data/preview` | Dataset preview |
| GET | `/analysis/promotion-effect` | Promotion effect analysis |
| GET | `/analysis/promotion-effect-dml` | DML promotion effect analysis |
| POST | `/allocation/optimize` | Budget-constrained discount allocation |

## API Documentation

After starting either backend, open:

- API documentation: http://127.0.0.1:8000/docs
- Health check: http://127.0.0.1:8000/health

Only one backend should use port 8000 at a time unless a different port is configured.

## Week 3: Discount Budget Optimization

### Objective

Build a constrained optimization module that allocates customer discounts using treatment-effect estimates from the causal inference pipeline.

### Implementation

- Uses SciPy's SLSQP optimizer.
- Reads `data/treatment_effects.csv`.
- Restricts optimized discounts to the range 0%–35%.
- Applies a total discount-allocation constraint based on the sum of existing discount fractions.
- Saves results to `data/optimized_discounts.csv`.
- Includes validation checks in `Karan/causal_ml/test_budget_optimizer.py`.

### Current Validation

The Week 3 implementation report records:

- 500 rows processed.
- No missing optimized discount values.
- All optimized discounts are within 0%–35%.
- The allocation satisfies the configured budget constraint.
- Automated validation checks pass.

### Limitations

The current objective is a simplified treatment-effect-based proxy. It does not yet maximize validated revenue or profit. The discount budget is a sum of discount fractions rather than a monetary budget. Further business-objective modelling and evaluation are required before these allocations can be used for real pricing decisions.

## Run Automated Tests

### Original Backend Tests

Run from the project root:

```bash
python -m unittest test_dml_model.py test_api.py test_api_validation.py test_discount_optimizer.py -v
```

### Integrated Backend Tests

Run from the project root:

```bash
python -m unittest discover -s backend-local -p "test_main.py" -v
```

## Important Model Limitations

- The pricing dataset is synthetic and may not represent real customer behavior.
- DML-style estimates depend on modelling choices and causal identification assumptions.
- Predictive discount recommendations are not proof of causal effects.
- Estimated revenue per record is not profit.
- Model outputs are not guarantees of real-world business results.

## Expected Outcome

The platform aims to identify customers whose behavior may change following an intervention. By studying treatment effects and comparing discount strategies, EconoCausal provides a foundation for more informed pricing and marketing decisions.

The project is an academic and internship development project. Its outputs require further validation before real-world deployment.
