





# Member 4 — Data Processing and Discount Optimization

## Responsibilities

This module prepares retail customer data for causal analysis and
optimizes discount offers subject to a marketing budget.

## Components

### Data processing
- `data_processing/data_loader.py`: Loads and saves CSV datasets.
- `data_processing/data_validator.py`: Validates required columns,
  numeric values, customer IDs, treatment labels, and outcomes.
- `data_processing/preprocessing.py`: Prepares features, treatment,
  and outcome variables for causal ML.