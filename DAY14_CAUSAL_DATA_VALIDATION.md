# Day 14: Causal Data Validation Report

## 1. Objective

The objective of this validation is to inspect the EconoCausal dataset before proceeding with causal graph specification and causal effect estimation.

## 2. Dataset Overview

- Dataset file: `data/pricing_data.csv`
- Total records: 2,000
- Total columns: 7
- Missing values: 0 across all columns
- Unique customer IDs: 2,000

### Variables

| Variable | Role in initial causal analysis |
|---|---|
| `customer_id` | Record identifier; excluded as a causal control by default |
| `price` | Candidate confounder |
| `discount` | Treatment |
| `competitor_price` | Candidate confounder |
| `promotion` | Candidate confounder |
| `season` | Candidate confounder |
| `purchase` | Binary outcome |

These roles are preliminary and depend on the actual data-generating process and timing of the variables.

## 3. Data Quality Checks

- `purchase` contains 1,648 records with value 0 and 352 with value 1.
- Overall purchase rate: 17.6%.
- `promotion` contains 1,403 records with value 0 and 597 with value 1.
- `season` contains three observed categories: `low`, `medium`, and `high`.
- `discount` ranges from 0.0 to 0.35.
- No missing values were detected in any column.

The checks support basic dataset completeness and validity. They do not establish causal identification.

## 4. Descriptive Findings

### Promotion groups

| Promotion | Records | Average discount | Purchase rate |
|---|---:|---:|---:|
| 0 | 1,403 | 0.1733 | 0.1411 |
| 1 | 597 | 0.1709 | 0.2580 |

Records with a promotion have a higher observed purchase rate. The average discounts are similar between these groups.

### Season groups

| Season | Records | Average discount | Purchase rate |
|---|---:|---:|---:|
| High | 590 | 0.1706 | 0.2085 |
| Low | 588 | 0.1776 | 0.1344 |
| Medium | 822 | 0.1705 | 0.1825 |

Observed purchase rates differ across seasons. This supports investigating season as a potential predictor and possible confounder, subject to a justified causal model.

### Purchase outcomes and numerical variables

| Purchase | Records | Average price | Average competitor price | Average discount |
|---|---:|---:|---:|---:|
| 0 | 1,648 | 574.882 | 570.107 | 0.165 |
| 1 | 352 | 448.013 | 448.537 | 0.209 |

Purchasers have lower average prices and higher average discounts in this dataset. These differences are descriptive associations and may reflect multiple factors.

## 5. Initial Causal Specification

- **Treatment:** `discount`
- **Outcome:** `purchase`
- **Candidate adjustment variables:** `price`, `competitor_price`, `promotion`, `season`

The proposed adjustment set is a starting hypothesis, not a verified sufficient adjustment set. We must examine whether these variables precede treatment and whether any could be affected by the discount decision.

## 6. Limitations

1. The dataset is synthetic and may not represent real customer behavior.
2. Descriptive group comparisons do not estimate causal effects.
3. Unmeasured factors may influence both discount assignment and purchase.
4. The causal graph's arrows require justification from the data-generating process and business context.
5. Positivity, conditional exchangeability, and consistency have not yet been established.
6. No DoWhy identification or refutation tests have been run as part of this validation.

## 7. Next Steps

1. Review the data-generation logic to understand how prices, discounts, promotions, seasons, and purchases are produced.
2. Refine the DAG and adjustment set using those assumptions.
3. Implement the graph in a compatible causal-analysis environment.
4. Estimate effects and run appropriate robustness checks.
5. Compare the causal analysis with the existing DML-style model without claiming that either method proves causality by itself.

## 8. Conclusion

The dataset passes the initial completeness checks and contains variation in the treatment, outcome, and candidate adjustment variables. The observed patterns motivate further analysis but do not establish causal effects. Additional work is required to justify the graph and assess identification assumptions.