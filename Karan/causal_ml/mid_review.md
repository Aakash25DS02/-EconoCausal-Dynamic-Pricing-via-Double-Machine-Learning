# EconoCausal – Mid-Project Report
## Member 2: Causal Machine Learning
**Coverage: Week 1 and Week 2**

## 1. Project objective

EconoCausal is a dynamic pricing project that uses Causal Machine Learning to understand whether offering a discount actually changes a customer's purchasing behaviour.

Traditional Machine Learning predicts which customers are likely to purchase. Causal Machine Learning goes further and estimates how a customer's purchase probability may change when a discount is offered.

My responsibility as Member 2 is to develop the causal inference component using DoWhy and EconML.

---

# WEEK 1 – Causal Graphing and Data Understanding

## 2. What was the objective?

The objective of Week 1 was to understand the relationships between discounts and customer purchases and identify variables that could influence both.

For this, I used DoWhy to create a Directed Acyclic Graph (DAG).

## 3. Understanding the variables

Our dataset contains 2,000 customer records and seven columns.

| Variable | Role | Meaning |
|---|---|---|
| customer_id | Identifier | Unique customer identification |
| discount | Treatment | Discount offered to the customer |
| purchase | Outcome | Whether the customer purchased (0 or 1) |
| price | Confounder / adjustment variable | Product price |
| competitor_price | Confounder / adjustment variable | Competitor's product price |
| promotion | Confounder / adjustment variable | Other promotional activity |
| season | Confounder / adjustment variable | Seasonal influence |

**What is a treatment?**

A treatment is the action whose effect we want to measure. In this project, the treatment is the discount offered to a customer.

**What is an outcome?**

An outcome is the result we want to study. Here, it is whether the customer makes a purchase.

**What is a confounder?**

A confounder is a variable that may influence both treatment assignment and the outcome. If we fail to account for relevant confounders, our estimated causal effect may be misleading.

## 4. What is a DAG?

A Directed Acyclic Graph represents our assumptions about the causal relationships between variables.

Our proposed structure is:

- Price → Discount
- Price → Purchase
- Competitor Price → Discount
- Competitor Price → Purchase
- Promotion → Discount
- Promotion → Purchase
- Season → Discount
- Season → Purchase
- Discount → Purchase

The main relationship we want to investigate is:

**Does changing the discount cause a change in purchase probability?**

## 5. Files created or used in Week 1

| File | Purpose |
|---|---|
| `Karan/causal_ml/dowhy_causal_dag.py` | Creates the causal model, defines treatment, outcome and adjustment variables, and identifies the causal estimand. |
| `Karan/causal_ml/causal_design.md` | Documents the causal design and modelling assumptions. |
| `Karan/causal_ml/week1_causal_assumptions.md` | Documents assumptions used in the causal analysis. |
| `Karan/causal_ml/dataset_understanding.md` | Documents the dataset and its variables. |
| `Karan/causal_ml/validate_pricing_data.py` | Checks the dataset for missing columns, invalid values and duplicate records. |

## 6. Actual Week 1 execution results

I executed:

`python Karan/causal_ml/dowhy_causal_dag.py`

The output showed:

- Records used: 2,000
- Treatment: discount
- Outcome: purchase
- Adjustment variables: price, competitor_price, promotion and season
- Identified estimand: Non-parametric Average Treatment Effect (ATE)
- Backdoor identification: Successfully identified

DoWhy identified a backdoor adjustment strategy using the four specified adjustment variables.

It also reported that no instrumental-variable or frontdoor identification strategy was available in the specified graph. These were not execution errors.

**Important understanding:** A DAG describes the causal assumptions of the model. It does not prove that hidden confounders do not exist.

---

# WEEK 2 – Double Machine Learning and Individual Treatment Effects

## 7. What was the objective?

The objective of Week 2 was to implement Double Machine Learning (DML) using EconML and estimate how a change in discount affects purchase probability.

Instead of estimating only one average effect, we wanted to estimate different treatment effects for different customers.

This is called Individual Treatment Effect (ITE) estimation.

## 8. What is Double Machine Learning?

Double Machine Learning is a causal inference method that uses Machine Learning models to estimate nuisance relationships involving treatment and outcome.

In our implementation, EconML's `LinearDML` uses two Random Forest models:

**Model 1 – Outcome model (model_y)**

Estimates the relationship between customer characteristics and the purchase outcome.

**Model 2 – Treatment model (model_t)**

Estimates the relationship between customer characteristics and the discount treatment.

DML uses these estimates to account for observed covariates when estimating the treatment effect.

## 9. Algorithms and libraries used

| Technology | Purpose |
|---|---|
| EconML | Causal Machine Learning framework |
| LinearDML | Double Machine Learning estimator |
| RandomForestRegressor | Outcome and treatment nuisance models |
| Scikit-learn | Data splitting and evaluation |
| Pandas | Data loading and processing |
| NumPy | Numerical calculations |

Our treatment variable is `discount`, and our outcome variable is `purchase`.

The adjustment features are:

- Price
- Competitor price
- Promotion
- Season

## 10. What is Individual Treatment Effect?

ITE estimates the difference between the outcome under two treatment levels for an individual customer.

For example:

A customer currently receives a 10% discount. We want to estimate how their purchase probability may change if the discount increases to 20%.

The model estimates:

**ITE = Estimated purchase probability at 20% discount − Estimated purchase probability at 10% discount**

A positive result indicates an estimated increase in purchase probability. A negative result indicates an estimated decrease.

These estimates are model-based and do not guarantee an actual purchase.

## 11. Files created or used in Week 2

| File | Purpose |
|---|---|
| `Karan/causal_ml/treatment_effect_analysis.py` | Main Week 2 implementation. Loads data, trains EconML LinearDML and estimates individual treatment effects. |
| `Karan/causal_ml/effect_summary.py` | Calculates the mean, median, standard deviation, minimum and maximum treatment effects. |
| `data/pricing_data.csv` | Historical/synthetic pricing dataset used to train and evaluate the causal model. |
| `data/treatment_effects.csv` | Stores the estimated treatment effects generated by the original Week 2 script. |

## 12. Actual Week 2 execution results

I executed:

`python Karan/causal_ml/treatment_effect_analysis.py`

The model used 2,000 records and split them into:

- Training records: 1,500
- Test records: 500

### Outcome prediction evaluation

| Metric | Result |
|---|---:|
| RMSE | 0.3784 |
| R² | 0.0297 |

These metrics evaluate the separate Random Forest outcome predictor. They should not be interpreted as the accuracy of the estimated causal effects.

### Treatment-effect summary

| Metric | Result |
|---|---:|
| Valid estimates | 500 |
| Mean treatment effect | 0.0601 |
| Median treatment effect | 0.0626 |
| Standard deviation | 0.0498 |
| Minimum treatment effect | -0.0588 |
| Maximum treatment effect | 0.1800 |

The mean estimated treatment effect was:

**0.0601 = approximately 6.01 percentage points.**

This means the model estimated an average increase of approximately 6.01 percentage points in purchase probability when the discount was increased by 10 percentage points, for the 500 test customers.

These results come from a synthetic dataset and should not be presented as proven real-world causal impact.

---

# MID-PROJECT REVIEW – DOWHY REFUTATION TESTS

## 13. Why do we perform refutation tests?

After estimating a causal effect, we need to check whether the result remains reasonably stable under certain changes to the data or treatment.

DoWhy provides refutation methods for this purpose.

I implemented two tests in:

`Karan/causal_ml/dowhy_refutation_tests.py`

### Test 1 – Random Common Cause

DoWhy adds a randomly generated common cause and checks whether the estimated effect changes substantially.

Actual output:

| Metric | Result |
|---|---:|
| Original estimated effect | 0.632000 |
| New estimated effect | 0.631941 |
| Reported p-value | 0.86 |

The estimated effect remained almost unchanged after adding the random common cause.

### Test 2 – Placebo Treatment

DoWhy replaces the actual treatment with an artificial placebo treatment and checks whether it produces an effect close to zero.

Actual output:

| Metric | Result |
|---|---:|
| Original estimated effect | 0.632000 |
| Placebo estimated effect | 0.013165 |
| Reported p-value | 0.84 |

The placebo estimate was much closer to zero than the original estimate.

These results are encouraging refutation checks, not mathematical proof that the original causal assumptions are correct.

**Important technical distinction:** This DoWhy refutation script estimates an ATE using backdoor linear regression. It does not directly refute the EconML LinearDML model.

---

# 14. Overall Week 1 and Week 2 summary

| Work | Result |
|---|---|
| Pricing dataset understanding | 2,000 records inspected |
| Dataset validation | Passed |
| DoWhy causal DAG | Executed successfully |
| Treatment and outcome identification | Completed |
| Confounder adjustment | Defined |
| EconML LinearDML | Executed successfully |
| Random Forest nuisance models | Used |
| Individual treatment effects | 500 estimates generated |
| Treatment-effect summary | Generated |
| Random common cause refutation | Executed |
| Placebo treatment refutation | Executed |

## 15. Final conclusion

During Week 1, I established the causal structure of the EconoCausal project using DoWhy. I identified discount as the treatment, purchase as the outcome, and price, competitor price, promotion and season as adjustment variables.

During Week 2, I implemented Double Machine Learning using EconML's LinearDML and Random Forest nuisance models. I estimated individual treatment effects for 500 test customers and obtained an average estimated purchase-probability increase of approximately 6.01 percentage points for a 10-percentage-point discount increase.

I also implemented DoWhy refutation tests to examine the robustness of the identified causal relationship.

**The outcome of these two weeks is a working causal inference foundation for the next stage of the project: using customer-level treatment-effect estimates to support personalized discount allocation.**