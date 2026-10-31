





# EconoCausal — Member 4

## Role
Data Pipeline and Discount Optimization

## Responsibilities
- Load retail customer data.
- Validate required columns, values, and customer IDs.
- Prepare clean data for causal machine learning.
- Build a budget-constrained discount allocation optimizer.
- Test preprocessing and optimization functionality.

## Project Structure
- `data_processing/data_loader.py`: load and save datasets.
- `data_processing/data_validator.py`: validate input data.
- `data_processing/preprocessing.py`: prepare data for causal ML.
- `optimization/objective.py`: maximize incremental profit.
- `optimization/constraints.py`: budget and customer constraints.
- `optimization/discount_optimizer.py`: optimize offer selection.