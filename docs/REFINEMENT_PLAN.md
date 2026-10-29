# Refinement pass — 2026-10-29

User request: review errors/improvements and deliver an ultra-refined premium frontend with Framer Motion.

## Boundaries

Preserve measured model artifacts and the frozen experimental protocol. No model tuning or retraining in response to final metrics. Keep the local FastAPI app and its review/evidence/source functions. The application revision may differ from the original experiment source snapshot; immutable experiment records are not rewritten.

## Work

- Independent Python correctness review: malformed artifacts, initialization concurrency, cross-model population integrity, strict label validation. Fix reproduced defects with regressions.
- Replace imperative frontend with typed React/Vite components and Motion for React (formerly Framer Motion). Compile a distributable UI into the Python package; keep one-command local serving.
- Refine the established analytical desk: warm stone, deep ink/green, restrained brass, locally hosted editorial serif headings and Plex interface text. Real evidence and precise tabular typography lead the composition.
- Correct stale export/detail behavior. Bind visible results and downloads to the successful current query. Date changes reset outcome reveal.
- Desktop buyer inspector; accessible mobile sheet with Escape, focus restoration and previous/next buyer controls.
- Make evidence scope explicit, compare cohort AP with base rates, show revealed population order rate, and keep exact chart values available.
- Add real view URL/history, filter clearing, deliberate skeleton/error/empty states and useful prediction-window context.

## Motion thesis

Focal interaction: explicitly revealing the next seven days changes a historical forecast into an observed outcome. A short masked reveal and status transition explain that boundary without delaying access.

Continuity: shared navigation indicator, selected buyer/detail transition and mobile inspection sheet. Feedback: 120–220ms control and panel transitions. Avoid fabricated intermediate statistic values, row-by-row delays, decorative looping and scroll choreography. Respect reduced motion through MotionConfig/useReducedMotion and CSS; preserve meaningful state labels.

## Verification gates

Python regressions and actual artifact verification; TypeScript production build and focused frontend request-state tests; desktop/tablet/mobile browser checks including normal/reduced motion, network failure/retry, query races, export freshness, mobile focus/keyboard and exact chart data. Capture in one batch, correct material findings in one batch, then confirm. Refresh TODO/MEMORY/BUGS/TRAPS/design and verification records.
