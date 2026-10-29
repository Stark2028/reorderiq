# ReorderIQ

## Platform and stack

Local web application served by Python/FastAPI with a typed React frontend, Vite 8 production assets and Motion for React (formerly Framer Motion). Artifact-backed JSON and the Python SQL/ML pipeline remain authoritative. No external hosting or messaging integration.

## Users and purpose

A sales analyst inspects a historical queue of buyers likely to order within seven days. An interviewer can replay an old Monday, inspect pre-cutoff buyer history, reveal later outcomes and assess model evidence. Success means the analysis is understandable and every displayed number comes from a measured artifact.

## Product truth

Public UCI Online Retail II, UK giftware, 2009-2011, currency GBP. Pseudonymous numeric buyer IDs; many original customers were wholesalers. Observational purchase probability does not measure the effect of contact. No fabricated company names, conversion gains or synthetic fallback rows.

## Interaction contract

Review queue first. A historical date, model and capacity control the population. Search/cohort filters change that population and its summary. The selected buyer's history always ends before the snapshot. Outcomes are hidden until explicitly revealed and reset on a date change. Model evidence and source/method remain available from persistent navigation. Loading, missing-run, empty and failed-request states provide recovery.

## Design context

Desktop desk analysis is the primary scene, with a fully operable mobile review. The user explicitly requested an ultra-refined premium frontend and Framer Motion. The established desk is refined with warm stone, deep ink green, restrained brass, Instrument Serif headings and Plex data text. Light and dark themes share the same semantic hierarchy. The accepted project brainstorm and MASTER_PLAN.md settle the product purpose; docs/REFINEMENT_PLAN.md records the refinement scope.

## Refined interaction contract

Visible results and export links belong to the successful current query; stale responses never become current evidence. Queue errors disable exports and provide retry. Mobile inspection uses a native modal sheet with paging, Tab/Shift-Tab containment, Escape, scroll restoration and return focus. Date changes hide outcomes. URL/history retains views and review filters. Evidence explicitly evaluates the frozen development winner rather than following the exploratory queue selector. Cohort AP appears beside purchase prevalence; queue comparisons display eligible-population rates only after reveal.

## Motion and accessibility

Framer Motion provides shared navigation selection, short view/detail transitions, buyer-sheet continuity and an explicit outcome reveal. Numbers change directly to measured values. Reduced-motion preferences remove spatial transitions while preserving state labels. Small-text contrast, native form labels, keyboard navigation, mobile focus and error recovery are verified.
