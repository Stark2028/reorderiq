# ReorderIQ master plan

Created 2026-10-29, Asia/Calcutta. Status: accepted local implementation complete; verification in verification/VERIFICATION.md.

## Product and evidence

Predict the probability that an observed buyer places at least one eligible purchase in the next seven days. Produce a ranked review queue and a historical replay with outcomes hidden until requested. This is an observational purchase propensity project, not a causal outreach policy. No calls, emails or external writes occur.

Motivation: https://arxiv.org/html/2403.07843v1 describes predictive buying research performed during an internship at Udaan. This project is an independent public-data implementation, not a reproduction of private Udaan results or confirmation of the current internship team's scope.

Data: UCI Online Retail II, https://archive.ics.uci.edu/dataset/502/online+retail+ii . Approximately 1.07 million invoice lines from a UK giftware retailer, 2009-2011; many customers are wholesalers. Currency is GBP. Customer IDs do not establish that every buyer is a business. CC BY 4.0; credit the original source. Primary source files remain outside Git.

## Phase gates

0. Establish this plan, engineering records, packaging and contracts.
1. Download the official archive with a size bound; hash it; normalize line records and write a sequential exclusion audit. Aggregate qualifying merchandise lines to invoices. Preserve the original raw file. Exclude the final partially observed calendar day.
2. Generate weekly Monday snapshots with SQLite SQL aggregations. Eligibility: an observed qualifying purchase strictly before the snapshot, with recency no greater than 180 days. Labels: at least one qualifying order in [as_of, as_of + 7 days). Only fully matured labels enter evaluation. Historical tenure means time since first observed order, not account registration.
3. Compare recency ranking, empirical Bayes Gamma-Poisson repeat purchase, scaled logistic regression and histogram gradient boosting. Use fixed settings and random seed. Fit probability calibration on a later independent interval. Choose the model using mean weekly average precision on development folds only.
4. Freeze model selection and evaluate a final temporal holdout. Export all candidates, denominators, weekly metrics, calibration, buyer cohorts and paired temporal block bootstrap comparisons. Report improvements only if measured.
5. Serve immutable local run artifacts through FastAPI. Build a responsive review queue, model evidence view and buyer history/replay with outcomes explicitly revealed. Include honest loading, error, empty and missing-run states. No fake data fallback.
6. Verify temporal/metric invariants, full real-data pipeline, API, desktop/mobile browser behavior and reproducibility. Record measured results and limitations in handoff/report/model card. Provide local launch commands.

## Temporal protocol (version 1, fixed before data inspection)

Snapshot Monday at 00:00 in source wall time; the original source has no supplied timezone. History is strictly < snapshot. Target is [snapshot, snapshot + 7 days). No use of future returns, final lifetime totals, target-window order details or country changes.

| Fold | Model fit labels end by | Calibration snapshots | Evaluation snapshots | Purpose |
|---|---|---|---|---|
| dev_1 | 2010-12-06 | 2010-12-06 to before 2011-01-03 | 2011-01-03 to before 2011-03-07 | Development |
| dev_2 | 2011-03-07 | 2011-03-07 to before 2011-05-02 | 2011-05-02 to before 2011-07-04 | Development |
| final | 2011-07-04 | 2011-07-04 to before 2011-09-05 | 2011-09-05 to before 2011-12-05 | Final holdout |

Training snapshots begin 2010-04-05, after a history warmup. Every fit label must mature by the fit cutoff. Calibration labels must mature by evaluation start. Evaluation origins are weekly; models remain frozen within each fold. Earlier evaluation periods may become historical training data in later folds. This is a rolling-origin protocol, not a per-week refit. No random row splitting.

Model selection: equal-weight mean of development-fold weekly average precision, tie broken by Brier loss and stable model ID. Calibration is fit only in its own interval, on clipped logits using logistic regression. Models failing a valid fit stop the run. A one-class calibration interval is an explicit error.

## Data contract

Positive placed merchandise orders define the target. Cancellation invoices, nonpositive quantity/price, non-merchandise stock codes, invalid/missing IDs, invalid timestamps and exact duplicate lines are excluded with counted reasons. Duplicate-line removal is an operational rule, not proof each duplicate is a data-entry error. Returns do not retroactively delete a placed order. This target does not measure net retained purchases or profit.

Events: customer_id, invoice_id, ordered_at, amount_gbp, units, distinct_items. Features include observed tenure, recency, orders and spend over past 7/30/90/180 days, lifetime observed orders, basket statistics and historical interval cadence. No personal names or emails. Eligibility and features use only pre-snapshot data.

Audit amendment before modeling: 64 eligible source invoices have multiple timestamps, all within two minutes, with no customer conflicts. Permit same-day spans up to five minutes and timestamp the complete invoice at its last line. Reject multiple-customer, cross-day and longer-span conflicts. This prevents counting one invoice twice or exposing a later line before it was recorded.

## Metrics and uncertainty

Primary: mean weekly average precision (PR-AUC as average precision). Also Brier loss, ROC-AUC where defined, calibration bins/ECE, and weekly precision/recall/lift at capacities 50 and 100. Top-K uses min(K, eligible population); ties break by numeric customer ID. Always publish base rate, selected denominator and buyer-week count; repeated buyers are not independent people.

Final differences use paired four-week moving-block resampling of weekly metrics. This is a descriptive stability interval over the observed test weeks; short history and temporal dependence limit inference. No causal or population-wide significance claim. Report new-observed, occasional and frequent buyer cohorts; define cohorts using pre-snapshot history only.

## Architecture

Python package `src/reorderiq`: ingest -> SQLite SQL features -> temporal folds/models -> metrics -> immutable artifacts. Standard-library SQLite provides inspectable SQL without a separate database service. pandas/parquet store normalized data and predictions; scikit-learn/scipy provide models/calibration. FastAPI reads run artifacts only. The user-requested refinement adds a React/TypeScript/Vite frontend with Motion for React, compiled into the same-origin Python application. Prebuilt assets allow Python-only serving.

Artifacts: data audit + file hashes; config and code fingerprints; feature schema; development selection record written before final fitting; final per-buyer predictions; report JSON/Markdown; joblib model bundles; normalized orders for historical replay. Artifacts are local and treated as trusted outputs; never load untrusted pickle/joblib files.

## Accepted refinement — 2026-10-29

The user requested an error/improvement review and a highly refined premium frontend with Framer Motion. docs/REFINEMENT_PLAN.md records the implementation boundary and motion thesis. The pass adds typed current-query components, a mobile focus-managed buyer sheet, light/dark themes, explicit evidence scope/base rates, strict artifact/population/label validation and efficient static serving. Original experiment artifacts are preserved and independently reverified; no model tuning or retraining was performed. Application version 0.2 differs from the original experiment source snapshot by design.

## Original finish criteria and future scope

Deployment scope was subsequently authorized on 2026-10-29. A separate resource-bounded AWS container serves the verified frozen experiment through an additional HTTPS route on the existing EC2 host. No model tuning or experiment rerun is part of deployment. Preserve SagaAgent and document actual public verification and rollback in deploy/aws/README.md and verification/DEPLOYMENT.md.

Finish requires an actual UCI run, checked leakage boundaries, reported honest candidate results, working queue/replay and documented local launch. Infrastructure scale, live retailer data, outreach experiments, product recommendation, deployment and authentication are future work. Do not add them to the critical path.
