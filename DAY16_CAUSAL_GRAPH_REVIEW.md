# Day 16: Causal Graph Review



## 1. Objective



The objective of this review is to compare the existing conceptual causal graph with the synthetic data-generation process used by EconoCausal. The review identifies mismatches, clarifies assumptions, and determines what should be considered before revising the graph.



## 2. Files Reviewed



- `causal_graph.py` — Python code that generates the graph definition.

- `causal_graph.dot` — saved Directed Acyclic Graph (DAG).

- `CAUSAL_GRAPH_NOTES.md` — explanation of the original graph and its assumptions.

- `DAY14_CAUSAL_DATA_VALIDATION.md` — initial dataset validation findings.

- `DAY15_DATA_GENERATION_ANALYSIS.md` — analysis of the synthetic data-generation process.

- `generate_data.py` — source code defining the synthetic data-generating mechanism.



## 3. Existing Conceptual Graph



The current graph includes the following directed edges:



- `price` → `discount`

- `price` → `purchase`

- `competitor_price` → `discount`

- `competitor_price` → `purchase`

- `promotion` → `discount`

- `promotion` → `purchase`

- `season` → `discount`

- `season` → `purchase`

- `discount` → `purchase`



The graph treats discount as the treatment and purchase as the outcome. The four other variables are proposed as potential confounders.



The existing Python code and saved DOT file contain the same edge definitions.



## 4. Comparison with the Synthetic Data Generator



The generator implements the following relationships:



1\. `price` is sampled independently from a uniform distribution between 100 and 1,000.

2\. `discount` is sampled independently from a uniform distribution between 0 and 0.35.

3\. `competitor_price` is calculated as `price` multiplied by an independently sampled random factor between 0.8 and 1.2.

4\. `promotion` is sampled from a Bernoulli distribution with probability 0.3.

5\. `season` is sampled independently, with probabilities of 0.3 for low, 0.4 for medium, and 0.3 for high.

6\. A season-dependent effect is calculated internally: 0 for low, 0.25 for medium, and 0.55 for high.

7\. Purchase probability is calculated from discount, price, promotion, the competitor-price-to-price ratio, and the season-dependent effect.

8\. `purchase` is sampled from a Bernoulli distribution using the calculated purchase probability.



The purchase log-odds formula is:



`log_odds = -2 + 5 × discount - 0.002 × price + 0.8 × promotion + 0.8 × (competitor_price / price - 1) + season_effect`



The purchase probability is the logistic transformation of this value.



## 5. Main Findings



### 5.1 Discount assignment



The generator samples discount independently of price, promotion, season, and the random factor used to construct competitor price. Therefore, it does not intentionally implement the four incoming arrows to discount shown in the original conceptual graph.



These arrows may still represent a separate real-world business hypothesis, but they are not relationships explicitly programmed into this synthetic generator.



### 5.2 Price and competitor price



Competitor price is generated from price and an independent random multiplier. This supports representing `price` as a parent of `competitor_price` in a graph intended to describe the synthetic generation process.



The generator also uses the competitor-price-to-price ratio in the purchase probability formula. The ratio is a derived quantity, not a separate column in the saved dataset.



### 5.3 Purchase outcome



The generator explicitly makes purchase probability depend on discount, price, promotion, competitor-price ratio, and season effect. A simplified graph can represent these relationships with arrows from the corresponding variables to purchase.



The internal season effect is not a separate dataset column. A graph using only the observed columns can represent the programmed season relationship as `season` → `purchase`.



### 5.4 Customer identifier



`customer_id` is a sequential record identifier. The generator does not use it to calculate discount, purchase probability, or purchase. It should not be treated as a substantive cause in the graph.



## 6. Confounding and Adjustment Implications



The synthetic generator does not intentionally create common causes of discount and purchase among the sampled variables, because discount is independently sampled.



Price, promotion, season, and competitor price are included in the purchase-probability calculation, so they are outcome predictors in the synthetic mechanism. However, predicting the outcome is not the same as being a confounder.



The distinction matters: adjustment variables should be selected using a justified causal model, not solely because they are associated with the outcome.



The existing DML-style model adjusts for several of these variables. That adjustment can be retained for model comparison, but the chosen variables should not automatically be described as verified confounders for this synthetic design.



## 7. Limitations and Uncertainties



1\. The generator describes a synthetic mechanism, not a verified real-world pricing process.

2\. A conceptual business DAG may intentionally express assumptions different from the generator's implementation.

3\. The generator's construction alone does not establish that the real-world causal assumptions are valid.

4\. Rounding of stored variables may affect exact numerical relationships.

5\. The graph review does not prove conditional exchangeability, positivity, consistency, or correct model specification for real-world data.

6\. No causal estimation or refutation test is performed by this documentation review.



## 8. Recommended Next Steps



1\. Keep the original conceptual graph documented as a preliminary business hypothesis.

2\. Decide whether to maintain a separate graph specifically describing the synthetic data-generating process.

3\. If a synthetic-mechanism graph is created, represent the programmed relationships accurately, including `price` → `competitor_price`, the outcome dependencies, and the independent assignment of discount.

4\. Update the graph notes to distinguish confounders from outcome predictors.

5\. Validate any revised graph against `generate_data.py` before using it in causal estimation.

6\. Continue to label model-based results as exploratory and avoid presenting synthetic results as proof of real-world causality.



## 9. Conclusion



The existing graph files agree with each other, but the graph's discount-assignment assumptions do not match the synthetic generator. The generator samples discount independently and explicitly models purchase probability using discount and several other variables. The review recommends clarifying whether the project needs a conceptual business DAG, a synthetic data-generating DAG, or both before making structural changes.



No graph files or model code were modified as part of this review.

