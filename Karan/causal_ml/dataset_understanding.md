# Dataset Understanding — EconoCausal

## Work Completed
- Reviewed the retail customer dataset structure.
- Identified the columns relevant to causal ML.
- Started understanding the treatment, outcome, and customer features.

## Key Variables
- Treatment-related variables: `treatment`, `discount_amount`
- Potential outcomes: `profit`, `revenue`, `purchased_again`, `churned`
- Customer features: `age`, `tenure_months`, `past_purchases`, `avg_order_value`, `price_sensitivity`, `website_visits_30d`, `days_since_last_purchase`, `cart_abandonment_rate`

## Questions to Verify
- How were discounts assigned to customers?
- Were customer features measured before discounts were assigned?
- How are profit and revenue calculated?
- What is the source of the dataset?

## Next Steps
- Confirm dataset definitions and treatment assignment.
- Assess whether the data supports causal analysis.
- Finalize the treatment, outcomes, and confounders before model estimation.

No causal conclusions have been established at this stage.
