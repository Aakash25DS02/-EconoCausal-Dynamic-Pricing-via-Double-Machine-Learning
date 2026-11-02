# Day 20 - Integration Validation Report



## 1. Objective



The objective of Day 20 was to verify that the EconoCausal components work together correctly through automated testing and live API execution.



## 2. Dataset Integration



Both the FastAPI application and the discount optimizer use the same dataset:



`data/pricing_data.csv`



- Dataset exists: Yes

- API and optimizer paths match: Yes

- Total records: 2,000

- Total columns: 7

- Missing values: 0



## 3. Automated Testing



The complete existing test suite was executed.



Command:



`python -m unittest test_dml_model.py test_api.py test_api_validation.py test_discount_optimizer.py -v`



Result:

- Total tests: 16

- Passed: 16

- Failed: 0

- Errors: 0



## 4. Live API Validation



The FastAPI application was started using:



`python -m uvicorn app.main:app --reload`



Application startup completed successfully.



The following endpoints were tested through Swagger and the browser:



| Endpoint | HTTP Status | Result |

|---|---|---|

| GET / | 200 | Passed |

| GET /health | 200 | Passed |

| GET /data/summary | 200 | Passed |

| GET /data/preview | 200 | Passed |

| GET /discount/recommendation | 200 | Passed |



## 5. Dataset Summary Results



- Total observations: 2,000

- Total columns: 7

- Purchase rate: 0.176

- Average discount: 0.1726

- Average price: 552.55

- Discount range: 0 to 0.35

- Missing values: 0



## 6. Discount Recommendation Results



The recommendation endpoint successfully evaluated 36 discount scenarios.



Returned results:



- Recommended discount: 0.26 (26%)

- Predicted purchase probability: 0.2664035742

- Estimated revenue per record: 89.1387890179

- Observations: 2,000

- Scenarios evaluated: 36



Important note: This is a model-based predictive scenario recommendation. It is not a proven causal effect, profit calculation, or guarantee of real-world revenue.



## 7. Integration Validation Summary



The following components were successfully verified:



- Dataset integration between the API and optimizer

- DML model automated test

- API endpoint tests

- API input and dataset validation

- Discount optimizer tests

- FastAPI application startup

- Live endpoint responses

- Discount scenario recommendation



## 8. Conclusion



Day 20 integration validation was completed successfully.



All 16 automated tests passed, all five live API endpoints returned HTTP 200, and both the API and optimizer used the same dataset.



The EconoCausal application is functioning correctly in the tested environment.



These results validate the current software integration but do not establish causal identification or guarantee real-world business performance.

