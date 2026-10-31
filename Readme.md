# EconoCausal: Dynamic Pricing via Double Machine Learning

## The Problem

Traditional predictive ML models identify customers who are likely to leave or make a purchase, but they cannot determine whether a marketing offer will actually change their behavior. As a result, businesses may waste money offering discounts to customers who would stay anyway or fail to target customers who could be persuaded.

## Week 3: Discount Budget Optimization

### Objective

Build a constrained optimization module that allocates customer discounts using treatment-effect estimates from the Week 2 causal inference pipeline.

### Implementation

- Uses SciPy's SLSQP optimizer.
- Reads `data/treatment_effects.csv`.
- Restricts optimized discounts to the range 0%–35%.
- Applies a total discount-allocation constraint based on the sum of existing discount fractions.
- Saves results to `data/optimized_discounts.csv`.
- Includes validation checks in `Karan/causal_ml/test_budget_optimizer.py`.

### Current Validation

- 500 rows processed.
- No missing optimized discount values.
- All optimized discounts are within 0%–35%.
- The allocation satisfies the configured budget constraint.
- Automated validation checks pass.

### Limitations

The current objective is a simplified treatment-effect-based proxy. It does not yet maximize validated revenue or profit, and the discount budget is a sum of discount fractions rather than a monetary budget. Further business-objective modelling and evaluation are required before these allocations can be used for real pricing decisions.
