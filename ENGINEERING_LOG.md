# Engineering log

All entries: 2026-10-29, Asia/Calcutta.

| Boundary | Implementation / evidence | Decision or correction |
|---|---|---|
| Phase 0 | MASTER_PLAN, TODO, MEMORY, BUGS, TRAPS, AGENTS and package contracts | Isolate new project; freeze seven-day target, eligibility and three temporal folds before data inspection. |
| Phase 1 | Official download, two-sheet audit, 36,553 orders / 5,851 buyers | Invoice timestamp audit revealed 64 multi-minute invoices; aggregate once at last line. Record cleaning exclusions and conservative final-day cutoff. |
| Phase 2 | SQLite historical snapshots, 87 Mondays | Strict history/target predicates, mature windows, no future-dependent population and invoice-line count confusion. |
| Phase 3 | Four fixed candidates and independent sigmoid calibration | Avoid internal random early stopping; use one CPU thread for Windows execution. Persist development choice before final fit. |
| Phase 4 | Actual final holdout and source/artifact bundles | Boosting selected; AP .3132 vs Gamma-Poisson .2892. Publish all candidates, calibration and temporal instability in top-50 gains. No tuning after final outcomes. |
| Phase 5 | Read-only API and queue/replay/evidence/source client | No training on requests; hidden future fields; cancel stale client requests; source-aware GBP/IDs; explicit errors. |
| Phase 6 | 22 regression checks, 12 browser checks, artifact recomputation and wheel build | Sandbox permissions handled through approved tool execution. Independent review found chart label inheritance/size; corrected once and verified. |
| Handoff | Data/model cards, results, descriptive profile, exported figures, interview guide, requirements lock and CI | Three actual experiments produce identical prediction values. Preserve source hashes and document remaining generalization/causal/hosting limits. |

See BUGS.md for observed defects and TRAPS.md for anticipated risks and their controls. Verification records distinguish actual results from unexecuted hosted CI and clean-environment installation.
