# EconoCausal – Mid-Review Cheat Sheet
**Member 2 – Karan | Week 1 & Week 2**

## WEEK 1 – DoWhy Causal Graph

**Goal:** Identify whether discounts influence customer purchases.

- Library: DoWhy
- Dataset: 2,000 customer records
- Treatment: `discount`
- Outcome: `purchase`
- Confounders / adjustment variables:
  - `price`
  - `competitor_price`
  - `promotion`
  - `season`

**What I implemented:**
- Created a causal DAG.
- Defined treatment and outcome.
- Identified the backdoor adjustment estimand.
- Documented causal assumptions.

**File:** `Karan/causal_ml/dowhy_causal_dag.py`

**Result:** Backdoor estimand successfully identified.

## WEEK 2 – Double Machine Learning

**Goal:** Estimate how discounts affect individual customer purchase probability.

- Library: EconML
- Algorithm: LinearDML
- Outcome nuisance model: Random Forest Regressor
- Treatment nuisance model: Random Forest Regressor
- Treatment: `discount`
- Outcome: `purchase`

**Data split:**
- Total records: 2,000
- Training: 1,500
- Testing: 500

**Actual results:**

| Metric | Result |
|---|---:|
| RMSE | 0.3784 |
| R² | 0.0297 |
| Mean ITE | 0.0601 |
| Median ITE | 0.0626 |
| Minimum ITE | -0.0588 |
| Maximum ITE | 0.1800 |

**Main finding:** A 10-percentage-point discount increase was estimated to increase purchase probability by an average of approximately 6.01 percentage points among the 500 test customers.

**Main file:** `Karan/causal_ml/treatment_effect_analysis.py`

**Summary file:** `Karan/causal_ml/effect_summary.py`

## MID-PROJECT – DoWhy Refutation

**Goal:** Check the robustness of the causal estimate.

| Test | Original / New result | p-value |
|---|---|---:|
| Random common cause | 0.632000 → 0.631941 | 0.86 |
| Placebo treatment | 0.632000 → 0.013165 | 0.84 |

**File:** `Karan/causal_ml/dowhy_refutation_tests.py`

Both tests executed successfully. They provide supporting robustness checks, not proof of causality.

## IMPORTANT CONCEPTS

**DAG:** A graph showing assumed causal relationships.

**Confounder:** A variable that may influence both treatment and outcome.

**ATE:** Average Treatment Effect across a population.

**ITE:** Individual Treatment Effect for a particular customer.

**DML:** Uses machine learning to estimate nuisance relationships and isolate treatment effects under causal assumptions.

**DoWhy:** Defines causal assumptions and performs causal estimation and refutation tests.

**EconML:** Estimates heterogeneous causal effects using machine learning.

## FILES TO REMEMBER

| File | Purpose |
|---|---|
| `dowhy_causal_dag.py` | Causal graph |
| `causal_design.md` | Causal methodology |
| `week1_causal_assumptions.md` | Causal assumptions |
| `dataset_understanding.md` | Dataset documentation |
| `validate_pricing_data.py` | Dataset validation |
| `treatment_effect_analysis.py` | EconML DML implementation |
| `effect_summary.py` | ITE statistics |
| `dowhy_refutation_tests.py` | Causal robustness checks |

## 30-SECOND PRESENTATION

"My responsibility is Member 2 – Causal Machine Learning. In Week 1, I developed the causal DAG using DoWhy and identified discount as the treatment, purchase as the outcome, and four adjustment variables. In Week 2, I implemented EconML LinearDML using Random Forest nuisance models to estimate individual treatment effects. The average estimated effect for a 10-percentage-point discount increase was 6.01 percentage points on purchase probability. I also implemented DoWhy refutation tests to examine the robustness of the causal assumptions."

**Remember:** The results are from synthetic data, so they demonstrate the implementation rather than proven real-world customer behaviour.