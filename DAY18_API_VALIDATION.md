# Day 18 - API Validation and Error Handling

## Objective
Improve API reliability by adding automated tests for invalid and missing pricing datasets.

## New Validation Tests

1. Missing required columns returns HTTP 422.
2. Empty dataset returns HTTP 422.
3. Missing values in required columns return HTTP 422.
4. Missing dataset file returns HTTP 404.

## Test Execution

Command:

```cmd
python -m unittest test_dml_model.py test_api.py test_api_validation.py -v
```

## Result

- Total tests: 10
- Passed: 10
- Failed: 0
- Errors: 0
- Status: All tests passed.

## Conclusion
The existing DML and API tests continue to pass. The additional tests verify dataset validation and expected HTTP error responses. The original project dataset remains unchanged because the validation tests use temporary files.

