# EconoCausal — Presentation Outline



## Slide 1: Project Title



**EconoCausal: Dynamic Pricing via Double Machine Learning**



- Internship project

- Focus: Pricing analysis, causal inference concepts, and discount recommendation

- Technology: Python and FastAPI



## Slide 2: Problem Statement



- Businesses use discounts to influence purchase behavior.

- Predicting purchases does not by itself establish the causal effect of a discount.

- A pricing system should compare discount scenarios while clearly communicating uncertainty and limitations.



## Slide 3: Proposed Solution



- Analyze pricing and customer purchase data.

- Estimate a discount effect using a Double Machine Learning (DML)-style approach.

- Compare discount scenarios using predicted purchase probability and estimated revenue per record.

- Expose the analysis through a FastAPI backend.



## Slide 4: Technology Stack



- Python

- Pandas and NumPy

- FastAPI and Uvicorn

- CSV dataset

- Python unittest

- Git and GitHub



## Slide 5: System Architecture



1. Generate or load the synthetic pricing dataset.

2. Validate and summarize the dataset.

3. Run the DML-style discount effect estimator.

4. Compare discount scenarios with the optimizer.

5. Serve results through FastAPI endpoints.

6. Validate behavior using automated tests.



## Slide 6: Results



- Dataset size: 2,000 records

- Dataset columns: 7

- Missing values in the latest validation: 0

- Discount scenarios evaluated: 36

- Recommended discount from the current predictive optimizer: 26%

- Predicted purchase probability: approximately 26.64%

- Estimated revenue per record: approximately 89.14 in the dataset's monetary units



These are model-based results using synthetic data. The revenue estimate is not profit, and the recommendation is not a proven causal optimum.



## Slide 7: Testing and Demonstration



- Six automated tests passed in the latest validation.

- Demonstrate the API health endpoint.

- Show the dataset summary and preview endpoints.

- Show the discount recommendation endpoint.

- Open the interactive API documentation at `/docs`.



## Slide 8: Limitations and Future Scope



### Limitations



- The dataset is synthetic.

- Causal interpretation depends on identification assumptions.

- The optimizer estimates revenue, not profit.

- Real-world performance has not been established.



### Future Scope



- Evaluate on suitable real-world data.

- Strengthen causal validation and model evaluation.

- Add cost and profit information to discount optimization.

- Expand edge-case tests and input validation.



## Conclusion



EconoCausal is an end-to-end prototype combining pricing data analysis, a DML-style estimator, discount scenario comparison, a FastAPI backend, and automated testing. More validation is needed before real-world business use.

