# Portable project handoff

Application version: 0.2.0. Scientific protocol: v1, frozen before the recorded experiments.

## Project state

ReorderIQ is a complete local buyer reorder study and review application. Python/FastAPI serves prebuilt React/TypeScript/Motion assets. Source data and generated experiment runs are excluded from Git; run `python -m reorderiq.cli run` to acquire the official UCI data and reproduce the experiment, then `python -m reorderiq.cli serve`.

The official workbook contains 1,067,371 invoice lines, normalized to 36,553 eligible orders and 5,851 observed buyers. The recorded final holdout has 13 weekly origins, 39,754 buyer-weeks and 3,874 distinct buyers. Development selected gradient boosting; final mean weekly AP is .3132 and precision@50 .5923. These are observational purchase results, not evidence of outreach effects.

## Working procedure

- Read AGENTS.md, MASTER_PLAN.md, TODO.md, BUGS.md and TRAPS.md before editing.
- Keep scientific features strictly before the prediction cutoff and evaluate only matured labels.
- Preserve recorded model/data provenance. Do not tune repeatedly against the observed final holdout; use a new untouched source/period for subsequent model selection.
- Record reproduced defects and regression evidence in BUGS.md. Keep anticipated risks in TRAPS.md.
- Maintain typed current-query guards, inaccessible stale exports, mobile modal focus restoration and reduced-motion behavior.
- Use `npm run build` from frontend/ after interface edits. On Windows use scripts/build_distribution.ps1 for a clean wheel; verify it with scripts/verify_distribution.py.
- MEMORY.md is an optional detailed local execution log, intentionally ignored. This file and the checked-in engineering/verification documents provide the portable context.

## Verification

The recorded local refinement passes 42 Python regressions, four frontend request-state tests and twelve browser flows. The final distribution was inspected against current source. See verification/REFINEMENT.md and verification/refinement-summary.json for commands, results and limits. Hosted CI status is available through the repository's Actions workflow; local records preserve their original verification boundary.

## Remaining scope

The portfolio demo is deployed at https://reorderiq.65.0.103.235.sslip.io on the existing AWS host, in a separate read-only container. The original experiment was independently reverified inside the container and twelve public browser flows passed with no JavaScript errors. See verification/DEPLOYMENT.md and deploy/aws/README.md for evidence, limits and rollback. Live retailer validation, an outreach experiment, authentication, scheduled retraining and high availability remain future work. Public portfolio hosting does not establish production validation.
