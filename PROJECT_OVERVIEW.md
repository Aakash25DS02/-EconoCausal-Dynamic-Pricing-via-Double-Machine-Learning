\# EconoCausal — Project Overview



\## 1. Project Objective



EconoCausal is a dynamic pricing and causal analysis project designed to explore how discounts relate to customer purchase behavior. It combines machine learning, causal inference concepts, and a FastAPI backend to analyze pricing data and compare discount scenarios.



\## 2. Problem Statement



Traditional predictive models estimate which customers are likely to purchase, but prediction alone does not establish whether offering a discount changes a customer's behavior. Businesses need reliable analysis to evaluate pricing strategies and avoid relying only on purchase predictions.



\## 3. Proposed Solution



The project includes a Double Machine Learning (DML)-style estimator to estimate the relationship between discount levels and purchase outcomes while accounting for observed control variables. It also includes a discount scenario comparison module that evaluates predicted purchase probability and estimated revenue per record across different discount levels.



The current scenario optimizer is predictive; its recommendation is not proof of a causal effect.



\## 4. Technology Stack



\- Python

\- Pandas and NumPy

\- FastAPI

\- Uvicorn

\- CSV-based synthetic dataset

\- Python unittest framework

\- Git and GitHub



\## 5. Dataset



The synthetic pricing dataset contains 2,000 records and seven columns:



\- `customer\_id`

\- `price`

\- `discount`

\- `competitor\_price`

\- `promotion`

\- `season`

\- `purchase`



The dataset had no missing values during the latest validation.



\## 6. Main Features



\- API health check

\- Dataset summary and preview

\- DML-style discount effect estimation

\- Discount scenario comparison

\- Predicted purchase probability and estimated revenue per record

\- Interactive API documentation through Swagger UI

\- Automated tests for the model and API



\## 7. Validation Results



The API was started successfully, and the health, summary, preview, and discount recommendation endpoints were verified.



Six automated tests passed, covering the DML model, API health, dataset summary, data preview, discount recommendation, and unknown endpoint handling.



The current scenario comparison evaluated 36 discount levels. Its reported recommended discount was 26%, with a predicted purchase probability of approximately 26.64% and estimated revenue per record of approximately 89.14 in the dataset's monetary units.



These figures are model-based estimates using synthetic data, not guaranteed real-world results. The revenue estimate is not profit.



\## 8. Current Limitations



\- The dataset is synthetic rather than real customer data.

\- Causal interpretation depends on identification assumptions and appropriate validation.

\- The current revenue objective does not account for costs or profit margins.

\- Real-world performance has not been established.



\## 9. Future Scope



\- Improve model evaluation and causal validation.

\- Explore profit-based discount optimization.

\- Add stronger input validation and more edge-case tests.

\- Evaluate the system on suitable real-world data when available.

\- Prepare a final project presentation and demonstration.



\## 10. Conclusion



EconoCausal demonstrates an end-to-end prototype combining discount analysis, a DML-style estimation module, scenario comparison, a FastAPI backend, API documentation, and automated testing. Further validation is needed before applying its recommendations to real business decisions.

## 11. System Architecture

### Data Layer
The project uses `data/pricing_data.csv`, a synthetic dataset containing 2,000 records and seven columns related to pricing, discounts, promotions, seasons, and purchase outcomes.

### Analysis Layer
- `dml_model.py`: Implements a DML-style estimator to estimate the relationship between discount and purchase outcomes while accounting for observed control variables.
- `discount_optimizer.py`: Compares discount scenarios using predicted purchase probability and estimated revenue per record.
- `generate_data.py`: Generates the synthetic pricing dataset.

### API Layer
`app/main.py` provides a FastAPI application with endpoints for API health, dataset summary, data preview, and discount recommendation.

### Testing Layer
- `test_dml_model.py`: Tests the DML-style estimator.
- `test_api.py`: Tests the API endpoints and expected responses.

### Overall Flow
1. Generate or load the synthetic pricing data.
2. Analyze the dataset and estimate the discount–purchase relationship.
3. Compare discount scenarios using the optimizer.
4. Access supported analysis results through the FastAPI endpoints.
5. Validate the application using automated tests.

**Important distinction:** The DML-style estimator and the predictive discount optimizer serve different purposes. The optimizer's recommended discount is a model-based scenario result, not a proven causal optimum.

