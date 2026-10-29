# Analytical and engineering traps

| ID | Trap | Required control / evidence |
|---|---|---|
| T01 | Future orders leak into features or eligibility | Strict event timestamp < snapshot; mutation test adding future events cannot change prior features. |
| T02 | Incomplete future window turns unknowns into negatives | Explicit observation end; label_end <= observation_end. Drop final partial calendar day. |
| T03 | Invoice lines counted as orders | Aggregate to invoice-level events; repeat identical invoice lines do not create extra orders. |
| T04 | Cancellations/adjustments treated as purchases | Sequential exclusions with audit; positive merchandise placement target. |
| T05 | Random split or overlapping target windows leak labels | Weekly origins, fully matured training/calibration labels and explicit fold guards. |
| T06 | Final holdout used to choose model | Persist development-only selection before final fit/evaluation. |
| T07 | Calibration uses test outcomes | Fit sigmoid on separate chronological interval only. |
| T08 | Buyer disappearance treated as known churn | Target is observed platform order; inactivity is not permanent churn. |
| T09 | High purchase probability mistaken for outreach effect | UI/reports state observational probability; no causal uplift/revenue claims. |
| T10 | IDs/currency mistaken for Indian kirana records | Use Buyer <ID>, GBP and UK source labels. No invented identities. |
| T11 | Unstable top-K ties, tiny denominator or no positives | Stable numeric-ID tie break; actual selected denominator; undefined metrics are null. |
| T12 | Repeated buyer-weeks treated as independent people | Report unique buyers and buyer-weeks separately; time-block stability intervals. |
| T13 | Explainability presented as causality | Buyer descriptions are historical facts; global permutation importance is predictive association only. |
| T14 | Stale artifacts or silent synthetic fallback | Fingerprint inputs/config/code; run manifest; missing run is explicit HTTP 503. |
| T15 | Future history shown before replay reveal | API independently strips outcomes; buyer history ends strictly before snapshot. |
| T16 | First observed purchase called registration | Label as observed history / first seen, with left truncation limitation. |
| T17 | Calibrated score hides weaker model | Report all candidates and raw/calibrated probability metrics; publish losses honestly. |
| T18 | Raw data or models accidentally committed | Project ignore rules; raw/run directories ignored. |
| T19 | Historical rates fail under holidays or drift | Report weekly variation and a model frozen over the final test interval. |
| T20 | Repeated tuning contaminates final holdout | Protocol/config frozen before first run; any later model tuning requires a new untouched evaluation source/period. |
| T21 | Late HTTP results overwrite a newer query | Typed current-query resource key, immediate invalidation, AbortController and active-response guard; out-of-order promise tests. |
| T22 | Export appears current while its data is stale | No href during pending/failure/debounce; current-query CSV browser regression. |
| T23 | Mobile modal or navigation traps/loses focus | Native modal plus explicit Tab wrapping, Escape and trigger focus; post-entry heading focus and accessible icon labels. |
| T24 | Decorative motion hides evidence or violates reduced motion | Short state/continuity transitions, measured numbers update directly, reduced-motion config/hook/CSS and browser check. |
| T25 | Evidence scope/prevalence or rate-difference units are misleading | Frozen-model scope label; cohort base rates; eligible population rate on reveal; precision differences expressed as percentage points. |
| T26 | Application revision rewrites experimental provenance | Keep v1 source.zip/manifest immutable; document application v0.2 separately; independently rebuild original labels/features/metrics. |
| T27 | Stale cached HTML references removed build assets | No-cache HTML, immutable caching only for successful hashed assets, same-origin prebuilt distribution and package inspection. |
| T28 | Malformed artifact JSON becomes a 500 or concurrent loads duplicate work | Narrow shape/feature validation, recoverable503 and initialization Lock; API regressions. |
| T29 | Setuptools build cache ships removed UI files | Validated clean-build script; every wheel runtime file compared byte-for-byte to current source by distribution verification. |

## Implemented evidence (2026-10-29)

- T01–T05, T11, T15: temporal, cleaning/metric and API regression tests; `verify` independently rebuilds every final population/label/feature from accepted orders.
- T06–T07, T17, T20: development-only selection guard, separate fit/calibration partitions, persisted selection hash and all candidate/raw probability metrics. No final-results-driven hyperparameter changes were made.
- T08–T10, T12–T13, T16, T19: explicit data/model cards, source-aware UI, observed-tenure labeling, measured cohorts and descriptive temporal intervals. These controls document limits; they do not remove domain shift or identify causal effects.
- T14, T18: ignored raw/run directories, source/data/code hashes, immutable completed manifests, missing/tampered-artifact regression tests and source archive per final run.
