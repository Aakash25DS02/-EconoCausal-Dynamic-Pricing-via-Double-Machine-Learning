Causal ML Design — EconoCausal

1. Objective

Estimate the causal effect of customer discounts on purchasing behavior and profit, and investigate which customers benefit most from different discount levels.

2. Research Questions

- Do discounts increase customer profit?
- Do different discount amounts have different effects?
- Which customer characteristics influence the effect of a discount?

3. Variables

- Treatment: "discount_amount"
- Primary outcome: "profit"
- Secondary outcomes: "purchased_again", "revenue", "churned"
- Potential confounders: "age", "tenure_months", "past_purchases", "avg_order_value", "price_sensitivity", "website_visits_30d", "days_since_last_purchase", "cart_abandonment_rate"

Note: Final variables depend on dataset validation and the discount-assignment process.

4. Proposed Method

1. Inspect and validate the dataset.
2. Define a causal graph (DAG) and document assumptions.
3. Use DoWhy to define and identify the causal effect.
4. Use EconML to estimate heterogeneous treatment effects where appropriate.
5. Evaluate results using robustness checks and refutation tests.

5. Important Assumptions to Verify

- How were discounts assigned to customers?
- Were discounts randomized or based on customer characteristics?
- Are the potential confounders measured before the discount was offered?
- How are revenue and profit calculated?

6. Current Status

Dataset validation is pending. No causal conclusions have been established. The final treatment definition, estimation method, and assumptions will be updated after validation.