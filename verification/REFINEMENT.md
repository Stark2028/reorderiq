# Refinement verification — v0.2

Verified 2026-10-29, Asia/Calcutta. Python 3.12.10, Node 24.18.0. The local application now uses React/TypeScript, Vite 8.3.5 and Motion for React 14.7.1 (Framer Motion). Exact frontend dependencies are in frontend/package-lock.json; Python dependencies remain in requirements.lock.

## Correctness

`python -m pytest -q -W error -p no:cacheprovider --basetemp=.test-tmp-refined-final --junitxml=verification/refinement-pytest.xml`

**42 passed in 3.77s**, exit 0. Covers original scientific boundaries plus malformed artifact shapes, historical-feature declarations, concurrent initialization, exact cross-model buyer/date populations, strict binary labels, gzip and cache policies. No model tuning or retraining occurred.

`npm test -- --maxWorkers=1` from frontend/: **4 passed**, 1.16s. Real hook tests verify synchronous invalidation, aborted and out-of-order responses, failure/retry and cleared buyer selections. They prevent old data from becoming current evidence.

`python -m reorderiq.cli verify`: passed. All 13 original artifact hashes, 13 weekly populations and 39,754 historical buyer-week feature/label rows were independently checked; metrics for four candidates were recomputed. The v1 experiment and its source.zip remain immutable. Application v0.2 is a later revision, so its source fingerprint is expected to differ from the recorded experiment snapshot.

## Browser and visual review

`python scripts/browser_check.py`: **12 flows passed**, zero JavaScript page errors. Normal and reduced motion, outcome reveal/reset, date controls, model/capacity filters, current buyer detail, empty/error recovery, stale-export prevention, CSV, frozen-model evidence scope, chart keyboard inspection, browser history, light/dark themes and native mobile sheet behavior were exercised. Modal tests include paging, seven Tab presses, Escape, restored trigger focus and released body scrolling.

No page-level horizontal overflow at 1560, 1280, 1100, 1024, 768, 390 and 360px. Chart text is unstroked and its rendered size is checked. Captures/results are in refinement-browser/. True mobile viewport captures are distinguished from full-page captures. Frames wait for local fonts and the maximum authored transition, avoiding clipped masks or scrolled fixed-element artifacts.

A fresh reviewer assessed desktop/mobile/light/dark captures against the accepted analytical desk direction. One material contrast issue was corrected: light --subtle changed to #686f64, giving a minimum reviewed applicable ratio of 4.60:1. After recapture, the reviewer scored this fix resolved. The final ship verdict covers that scored fix; no broad certification is implied.

The design documenter wrote updated DESIGN.md and a schema-v2 .impeccable/design.json before its session ended. The primary agent validated the complete JSON, 48 color entries, 10 component records and the actual breakpoint/motion narrative. The unavailable design-launcher/FORM/approved-comp provenance remains disclosed rather than invented.

## Production build and distribution

`npm run build`: TypeScript check, Vite production build and package copy passed without warnings. Evidence and methodology views are lazy chunks. All fonts and runtime notices are locally bundled. `npm run format:check` passes; Python Ruff check/format passes.

`npm audit --omit=dev --json`: **0 reported runtime vulnerabilities**. This does not report a development-dependency audit or certify the application.

The clean package command is `scripts/build_distribution.ps1`. It validates the generated setuptools build path inside this project before cleaning it; this fixes a reproduced stale-build problem that retained the deleted vanilla frontend.

Final wheel: `reorderiq-0.2.0-py3-none-any.whl`, **387,414 bytes**, SHA-256 `02dba5d9d2ad999e0f958c1f6ff71b732bb1beb932de92eda05b8670ccd2a159`.

`python scripts/verify_distribution.py`: **passed**. All 36 shipped runtime files match current source byte-for-byte; 42 total wheel entries include compiled UI references, fonts and licenses, excluding raw data and model runs. Actual same-origin serving returns no-cache HTML, no-store APIs and one-year immutable caching for successful hashed assets. Entry JavaScript: 346,423 bytes decoded / **111,871 bytes transferred with gzip**. Evidence: distribution.json.

The Python server was restarted on port 8010 with API version 0.2.0 and the same verified experiment. Hosted CI and a fresh installation of the entire pinned environment have not been executed; the supplied CI workflow now includes frontend format/test/build checks. Live retailer validation, causal outreach experiments and production hosting remain outside this local refinement.
