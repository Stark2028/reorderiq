# Model card

## Intended use

Inspect historical seven-day purchase probabilities and compare a capacity-limited buyer review queue against transparent alternatives. Local portfolio/research application, not a validated live outreach system. Models cannot identify incremental purchases caused by calls.

## Fixed protocol and candidates

Protocol v1 was written before the first real-data experiment. Weekly Monday snapshots begin 2010-04-05 after a history warmup. Features aggregate strictly earlier observed orders: recency, observed tenure, order/spend windows, basket statistics and cadence. IDs and target-window information are excluded from model inputs.

- Recency: exponential transform of days since last order, preserving simple recency ranking.
- Gamma-Poisson: empirical Bayes repeat-event counts after the first observed order with observed exposure in days. Stationary purchase-rate assumption; no dropout or seasonality. Not the Udaan paper's modified model.
- Logistic: log1p numeric features, training-only standardization, fixed C=1, max_iter=1200.
- Histogram gradient boosting: 120 iterations, learning_rate=.07, max_leaf_nodes=15, l2=5, random early-stopping split disabled.

Every model receives a sigmoid calibration fit on clipped logits in an independent later interval. Negative slopes or missing calibration classes stop the experiment. No class reweighting, threshold tuning or hyperparameter search uses final outcomes.

| Fold | Fit labels mature by | Calibration | Evaluation |
|---|---|---|---|
| dev_1 | 6 Dec 2010 | 6 Dec–2 Jan | 3 Jan–6 Mar 2011 |
| dev_2 | 7 Mar 2011 | 7 Mar–1 May | 2 May–3 Jul 2011 |
| final | 4 Jul 2011 | 4 Jul–4 Sep | 5 Sep–4 Dec 2011 |

Earlier evaluation windows may become historical training data in later folds. Models stay frozen within each fold. Buyers can appear across time splits; this evaluates future periods for an observed buyer population, not generalization to entirely unseen entities. Model choice uses equal-weight development-fold mean weekly average precision, Brier tie break. The selection record is saved before final fitting.

## Measured final result

Selected: histogram gradient boosting. Final population: 39,754 buyer-weeks / 3,874 distinct buyers / 13 Mondays. Mean weekly AP .3132, Brier .0841, precision@50 .5923. Statistical Gamma-Poisson baseline: AP .2892, Brier .0854, precision@50 .5738. Logistic regression AP .3036.

Paired four-week moving-block resampling (1,000 repetitions, seed 20261029) against Gamma-Poisson: AP difference +.0240, descriptive 95% stability interval [.0210, .0295]; precision@50 difference +.0185, interval [-.0077, .0338]. This indicates limited observed-period stability for the queue-size improvement. The short 13-week history and temporal dependence limit inference; these are not causal or independent-buyer confidence claims.

All candidates and raw/calibrated probability metrics are published in the run report. Final results were not used to tune models. Subsequent implementation corrections concerned source timestamp handling, reporting/provenance and UI behavior; measured prediction values remained identical.

## Interpretation

Average precision summarizes ranking against observed purchase labels; it is not accuracy. Top-K uses the actual selected denominator, stable numeric-ID tie breaking and the same weekly population for each candidate. Lift is predictive enrichment over the eligible buyer order rate, not business uplift caused by contact. Calibration summarizes buyer-weeks, not independent people. Permutation importance uses a fixed sample of up to 4,000 final buyer-weeks, two shuffles per feature; correlated predictors share information, and effects are not causal.

## Limits and future validation

Historical UK giftware and many wholesale customers do not establish present Udaan performance. Target excludes returns/adjustments and does not model profit. First-seen histories are truncated. Holiday drift, missing-ID selection and buyers with very short histories remain risks. Cohort results are descriptive, not a fairness certification.

A future randomized experiment would compare contact policies under the same budget, with predefined order/revenue outcomes, contact costs and treatment assignment. Offline propensity metrics alone cannot determine whom a call would help. A new untouched period/source is needed for model changes made after viewing the final holdout.

## Artifacts and serving

Run bundles contain fitted models, calibrators, feature schema, source/data/code hashes, source archive, frozen selection and predictions. Joblib files are trusted local training outputs; never load untrusted bundles. The web server reads verified prediction artifacts rather than deserializing models or training during requests.
