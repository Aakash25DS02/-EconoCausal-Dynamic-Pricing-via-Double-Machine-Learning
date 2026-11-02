\# Day 15: Synthetic Data Generation Analysis



\## 1. Objective



Inspect `generate\_data.py` to understand how the EconoCausal synthetic dataset is created and identify implications for the preliminary causal graph.



\## 2. Dataset Reproducibility



The `generate\_pricing\_data()` function was executed with its default settings.



\- Default record count: 2,000

\- Default random seed: 42

\- Generated columns: `customer\_id`, `price`, `discount`, `competitor\_price`, `promotion`, `season`, `purchase`

\- Missing values in generated data: 0

\- Purchase rate: 0.176

\- Discount range: 0.0 to 0.35



The generated DataFrame and saved `data/pricing\_data.csv` were compared.



\- Same shape: True

\- Same column names: True

\- Exactly identical: True



This confirms reproducibility with the current code, dependencies, seed, and saved CSV.



\## 3. How the Variables Are Generated



\- `price` is sampled uniformly between 100 and 1,000.

\- `discount` is sampled uniformly between 0 and 0.35.

\- `competitor\_price` is calculated by multiplying `price` by a random factor between 0.8 and 1.2.

\- `promotion` is sampled from a binary distribution with probability 0.3 for value 1.

\- `season` is sampled from low, medium, and high categories with probabilities 0.3, 0.4, and 0.3.

\- `season\_effect` is 0 for low season, 0.25 for medium season, and 0.55 for high season.

\- `purchase` is sampled as a binary outcome using the calculated purchase probability.



\## 4. Purchase Probability Formula



The script calculates:



`log\_odds = -2.0 + 5.0 \* discount - 0.002 \* price + 0.8 \* promotion + 0.8 \* (competitor\_price / price - 1) + season\_effect`



It then applies the logistic transformation:



`probability = 1 / (1 + exp(-log\_odds))`



Finally, the purchase outcome is sampled using this probability.



The formula intentionally makes discount, promotion, competitor-price ratio, and season affect the calculated purchase probability. Price has a negative coefficient.



\## 5. Implications for the Causal Graph



\- The generated discount is sampled independently of price, promotion, and season in the data-generation code.

\- Competitor price depends on price and an independent random multiplier.

\- Purchase probability directly depends on discount, price, promotion, competitor-price ratio, and season effect.

\- Purchase is randomly sampled from the calculated probability.



These implementation details suggest that the synthetic data-generating process does not intentionally create confounding of the discount effect through price, promotion, or season. However, the graph must still reflect the intended timing and meaning of variables, and rounding and model specification should be considered.



\## 6. Limitations



1\. The dataset is synthetic and intended for pipeline testing.

2\. Its programmed relationships do not establish that the same relationships hold for real customers.

3\. Reproducibility and complete data do not establish causal validity.

4\. The existing causal graph is a hypothesis that should be checked against the data-generation logic.

5\. No DoWhy identification or refutation tests were performed in this analysis.



\## 7. Next Steps



1\. Review the existing causal graph and notes against the actual data-generation code.

2\. Clarify which variables are causes, derived variables, and outcomes in the synthetic process.

3\. Document any proposed graph changes before modifying the existing graph.

4\. Plan a compatible causal-analysis environment before implementing DoWhy identification and refutation tests.



\## 8. Conclusion



The synthetic dataset is reproducible and exactly matches the saved CSV. The data-generation code provides a clear, programmed relationship between the discount and purchase probability. This improves our understanding of the intended synthetic process but does not establish causal validity for real-world pricing decisions.

