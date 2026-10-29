# ReorderIQ working procedure

Read MASTER_PLAN.md, TODO.md, BUGS.md, TRAPS.md and docs/HANDOFF.md before continuing work. Read MEMORY.md when present; it is a local-only detailed handoff excluded from publication.
Implement one coherent phase at a time; update the checklist and handoff at phase boundaries.
Record real defects in BUGS.md with reproduction, correction and regression evidence.
Record anticipated analytical failure modes in TRAPS.md; do not call an unobserved risk a discovered bug.
Preserve the surrounding SagaAgent project. Work inside this directory.
Never fabricate results, model improvements, customers, outreach effects or revenue.
Features must use events strictly before the snapshot; labels cover [snapshot, snapshot + 7 days).
Choose models on development folds only. Freeze that choice before opening the final holdout.
Keep source data, machine-specific paths, virtual environments and generated runs out of source control.
Document exact reproduction commands, measured results and remaining limits in MEMORY.md.
Run meaningful regression checks for data contracts, temporal boundaries, evaluation and API behavior.
Use deterministic seeds, explicit versions and immutable run artifacts. Do not train inside HTTP requests.
Public GitHub source publication and application deployment on Vercel/AWS/Render were explicitly authorized on 2026-10-29. AWS deployment uses an isolated ReorderIQ container on the existing host; preserve SagaAgent, its data and its proxy route.
