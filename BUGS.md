# Observed defects

## B001 — Windows CPU discovery fails under strict warnings (fixed)

- Trigger: fit histogram gradient boosting under `pytest -W error` on this Windows host.
- Effect: joblib's physical-core discovery calls an unavailable Windows utility; a fallback warning becomes an exception.
- Fix: default `LOKY_MAX_CPU_COUNT=1` before model-library imports, respecting explicit caller overrides. Experiments additionally bound native thread pools to one. This also avoids Windows sandbox restrictions on joblib thread-pool named pipes.
- Regression: all four candidate-fitting tests pass under warnings-as-errors; 14 checks passed at this boundary.

## B002 — Single-timestamp invoice assumption rejected valid source records (fixed)

- Trigger: first official UCI preparation run stopped on 64 invoices with more than one timestamp.
- Inspection: no customer conflicts; all spans are at most two minutes (2,874 qualifying source lines before sequential deduplication).
- Effect: strict normalization rejected the whole dataset. Grouping by timestamp instead would incorrectly split orders.
- Fix: aggregate each invoice once at its last recorded line, accepting same-day spans <=5 minutes. Longer, cross-day or customer conflicts still stop ingestion.
- Regression: multi-minute invoice test checks one order, summed amount and last-line availability; conflict test remains.

## B003 — Chart text inherited icon strokes and shrank on mobile (fixed)

- Trigger: independent finish review of desktop/mobile evidence captures.
- Effect: chart axes inherited the global SVG stroke and appeared outlined; SVG scaling made mobile text about 7px.
- Fix: explicit `stroke:none` on chart text; 14 SVG-unit base / 19 mobile text; stack evidence charts below 1200px.
- Regression: browser checks assert unstroked text and rendered size >=11px on desktop/mobile. Reviewer scored this fix resolved after recapture. Its ship verdict covers the scored fix, not a fresh whole-surface audit.

## B004 — Malformed artifact document shapes escaped the recovery state (fixed)

- Trigger: a latest pointer containing a JSON array, or a non-string run ID, raised TypeError in artifact startup. A read-only reproduction returned HTTP 500 instead of the documented recoverable 503.
- Fix: explicitly validate JSON object shapes, run-ID types, manifest hash map, selected model/source, historical feature declarations and required table columns before publishing a store. Reject future-target fields masquerading as historical features. Preserve the existing API response shapes for valid runs.
- Regression: malformed latest-pointer and artifact-document parameterized tests return readiness=false / 503; a config declaring target as a historical feature is rejected.

## B005 — Parallel startup requests loaded the same experiment repeatedly (fixed)

- Trigger: initial metadata, evidence and queue requests could all observe an empty store and independently hash/load the same Parquet tables.
- Effect: duplicate startup allocation and I/O, despite all requests ultimately pinning the same experiment.
- Fix: serialize the initial artifact load with a thread lock and double-check the pinned store inside it. Later reads retain the fast cached path. Failed loads remain retryable.
- Regression: concurrent metadata/evidence/queue/status requests initialize a deliberately delayed store exactly once and all return 200.

## B006 — Evidence verification compared target arrays without buyer keys (fixed)

- Trigger: an alternate candidate could have every buyer ID reassigned while preserving sorted target values and metric totals. The previous verifier compared targets alone; it also did not require every declared candidate to be present.
- Fix: require the declared candidate set, unique (model, snapshot, buyer) rows and exact shared (snapshot, buyer) keys before comparing targets or recomputing metrics.
- Regression: consistent fixture passes; reassigned buyer IDs, missing candidates and duplicate buyer-weeks are rejected. The unchanged real four-candidate run still verifies all 13 weeks / 39,754 buyer-weeks.

## B007 — Fractional target labels were silently truncated before validation (fixed)

- Trigger: evaluate accepted labels such as [0.5, 1.9] because it converted them to integer [0, 1] before checking binary membership. The reproduction incorrectly reported one positive.
- Fix: validate the original labels against {0,1} before integer conversion. Missing and fractional labels now fail explicitly.
- Regression: fractional and NaN target cases are rejected. The existing measured artifacts contain valid binary labels and remain unchanged.

Review verification: `python -m pytest -q -W error -p no:cacheprovider tests/test_api.py tests/test_verify.py tests/test_ingest_metrics.py --basetemp=.test-tmp-review` — 29 passed in 3.14s. Ruff checks/format pass for the owned files. `python -m reorderiq.cli verify` passes on the original final run; no model fitting, parameters, predictions or reports were changed by these fixes.

## B008 — Failed filter requests left a stale CSV export available (fixed, v0.2)

- Trigger: load a queue, change a filter, then fail the replacement request.
- Effect: the previous export URL remained active while controls described the new query.
- Fix: current-query resource identity gates both visible data and the export URL; pending/failed queries have no download href. Debounced search also invalidates old results immediately.
- Regression: frontend late-response/failure tests and browser failure/retry/export checks verify that only a matching successful result can be exported.

## B009 — Previous buyer details remained visible during a replacement request (fixed, v0.2)

- Trigger: change selected buyer, historical date, model or reveal state while a detail request is pending.
- Effect: old details could appear under a new selection/context until replacement finished.
- Fix: detail identity includes buyer/date/model/reveal, with synchronous invalidation, abort and late-response guards. Loading/error views replace stale content.
- Regression: frontend tests resolve obsolete requests after current ones, clear selections and exercise failure/retry; browser verifies model/buyer alignment.

## B010 — Mobile inspection lost the queue position and keyboard return path (fixed, v0.2)

- Trigger: select a buyer on the original stacked mobile layout; the page jumps to the distant inspector with no return action.
- Fix: native modal buyer sheet with paging, close/Escape, body-scroll restoration and focus returned to the opening row. QA also found native Tab traversal could leave the expected document focus; explicit Tab/Shift-Tab wrapping now supplements showModal.
- Regression: browser checks modal paging, seven consecutive Tab presses, Escape, focus restoration and released body overflow.

## B011 — Navigation exit animation stole focus before the next view entered (fixed, v0.2)

- Trigger: navigate to a lazily loaded view during the previous view's Framer Motion exit.
- Effect: the old view consumed the focus flag, leaving the new heading unannounced.
- Fix: focus the heading after entry completes only when the rendered view matches the current URL. Compact icon navigation also has explicit accessible names.
- Regression: browser verifies the evidence heading receives focus and browser-back navigation restores the correct view.

## B012 — Refined light-theme secondary text missed small-text contrast (fixed, v0.2)

- Trigger: independent final review measured placeholders/ranks using light --subtle #757c71 against light surfaces.
- Effect: contrast was below 4.5:1.
- Fix: --subtle #686f64; minimum reviewed applicable contrast is 4.60:1, including selected rows.
- Regression: rebuilt production CSS, recaptured the same desktop/mobile views, and the reviewer scored the sole listed fix resolved. The final ship verdict covers that scored fix.

## B013 — Repeated wheel builds retained deleted frontend files (fixed, v0.2)

- Trigger: build the new distribution after removing the original vanilla frontend.
- Effect: setuptools reused build/lib from v0.1 and included deleted app.js/app.css in the wheel. The running React interface was correct, but the distribution contained obsolete code.
- Fix: scripts/build_distribution.ps1 validates the absolute generated build path inside this project, refuses reparse points, removes that output and performs an isolated wheel build.
- Regression: scripts/verify_distribution.py compares every packaged runtime file byte-for-byte with current source, checks bundled UI references/notices and verifies actual gzip/cache/version behavior.

## Test fixture correction

The initial synthetic candidate test assigned independent purchase rates and recency-based targets. Gamma-Poisson correctly triggered the negative calibration-slope guard. The fixture now provides aligned recency/repeat-frequency signal. The application guard is retained; this was not a real-data model failure.

Record each defect as: ID, status, trigger/reproduction, effect, root cause, fix, regression evidence.

## Refinement execution notes

- npm was configured for cache-only requests. The project-local dependency installation used an explicit writable cache and normal registry access; no global package installation was needed. One stalled install was stopped before its bounded replacement continued.
- Vite's optional Windows lightningcss binary initially failed to install. Reinstalling optional dependencies restored the native compiler; the production build then passed without warnings.
- Early full-page captures used a scrolled document and caught in-progress masks. The capture helper now resets full-page scroll and waits for fonts and the maximum authored transition; the mobile dialog uses a true viewport capture. These were evidence-capture defects, not fabricated application screenshots.

## Original execution notes

- Windows sandbox denied pytest temporary directories and Playwright subprocess pipes. Approved execution outside that sandbox passed all regression/browser checks.
- This host's Starlette TestClient warns that its HTTP client changed. API tests use httpx AsyncClient + ASGITransport directly, preserving warnings-as-errors without suppressions.
- First package-build attempt lacked a global setuptools backend under `--no-build-isolation`; normal isolated build requirements are the supported installation path. Package-build verification is recorded in verification/VERIFICATION.md.
- Initial source and cached-source prediction tables had identical values but different Parquet serialization bytes. Reproducibility compares actual tables and records hashes separately; no byte-equality claim is substituted for value equality.
