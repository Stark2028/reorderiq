# Interview notes

## 60-second explanation

"I built ReorderIQ to predict which observed buyers would place an order in the next seven days. The motivation came from published predictive-buying research at Udaan, but my dataset is public UK retail data. I cleaned about 1.07 million invoice lines into 36,553 positive merchandise orders, built historical SQL features, and compared recency, a Gamma-Poisson baseline, logistic regression and gradient boosting. I selected the model on two earlier temporal folds, calibrated probabilities in a later interval and evaluated a final untouched 13-week period. The selected model reached .313 mean weekly average precision and 59.2% precision in a top-50 review queue. A historical replay lets you inspect exactly what was known at prediction time and reveal later outcomes. The data cannot tell me whether calling those buyers would cause more orders."

Adapt this to your own understanding; do not claim stakeholder research, live customers, revenue gains or manual authorship of every implementation line. Implementation used Codex; explain the decisions and verification you actually understand.

## Decisions to defend

- Why predict an observed order instead of inventing a churn label? No purchase within seven days is observable; permanent churn is not.
- Why time splits? Random rows mix later purchasing behavior into earlier predictions. Training/calibration labels must also mature before the next partition.
- Why can a buyer appear across folds? The intended task is later behavior of an existing observed buyer, not acquisition of a new entity.
- Why average precision? Positive outcomes are relatively sparse; ranking quality matters to a capacity-limited review. Brier and calibration test probability quality separately.
- Why compare Gamma-Poisson? It is a transparent purchase-frequency model with a real statistical assumption; the selected ML model should justify extra complexity against it.
- Why not claim business uplift? Propensity does not identify the incremental effect of contact. Some high-scoring buyers might order anyway.
- What bug mattered? Some invoices have line timestamps one or two minutes apart. Count one invoice at its last line, rather than splitting it or exposing later amounts early.
- What remains weak? Old UK giftware source, missing buyer IDs, left-truncated history, seasonal drift and only 13 final test weeks. The top-50 gain against the statistical baseline is uncertain over time.

## Proposed resume wording, after personally reviewing the result

- Built a buyer reorder prediction pipeline on 1.07M public retail invoice lines using Python, SQLite SQL and scikit-learn; enforced historical feature cutoffs and independently calibrated seven-day purchase probabilities.
- Compared four candidates using chronological development folds and a 13-week final holdout; selected gradient boosting achieved .313 mean weekly average precision and 59.2% precision in a top-50 buyer review queue.
- Developed an interactive historical replay with pre-cutoff buyer histories, explicit outcome reveal and verified experiment artifacts; automated leakage, data-contract and API regression checks.

Avoid "59.2% accuracy", "increased revenue", "optimized Udaan sales", "causal uplift" or treating buyer-weeks as distinct customers.
