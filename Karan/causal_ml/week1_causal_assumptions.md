# Week 1 — Causal Design and Validation

## Objective
Study the relationship between discount level and customer purchase behavior.

## Dataset
- File: `data/pricing_data.csv`
- Rows validated: 2,000
- Validation status: Passed
- Treatment: `discount`
- Outcome: `purchase`

## Variables in the proposed DAG
- `price`
- `competitor_price`
- `promotion`
- `season`

The DAG currently assumes these variables may influence both discount and purchase. They are proposed adjustment variables, not confirmed confounders.

## Current implementation
- Data validation: `validate_pricing_data.py`
- DAG and estimand identification: `dowhy_causal_dag.py`
- DoWhy successfully identified a backdoor estimand.

## Assumptions and limitations
- The dataset is synthetic.
- The process assigning discounts must be checked.
- Adjustment variables should be measured before the discount is assigned.
- The DAG represents assumptions; it does not establish that those assumptions - The DAG represents assumptions; it does not establish ab- The DAG represents assumptions; it doeent initial caus- The DAG represents assumptions; it does not establish that those assumptaset fields and - The DAG represents assumptiond- The DAG represents hy - The DAG repreify the backdoor estimand
- [x] Recor- [x] Recor- [x] Reimit- [x] Recor- [x] Recor- [x] Reassignment lo- [x] Reciming of covariates
