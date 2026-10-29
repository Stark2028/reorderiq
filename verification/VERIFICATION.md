# Verification record

Verified 2026-10-29, Asia/Calcutta. Python 3.12.10 on Windows. Exact installed dependencies are pinned in requirements.lock. A fresh installation of all 47 pinned distributions in a clean virtual environment has not been performed; the project wheel itself was built and its bundled assets inspected.

## Regression suite

```powershell
python -m pytest -q -W error -p no:cacheprovider --basetemp=.test-tmp-final --junitxml=verification/pytest-results.xml
```

**22 passed in 2.37s**, exit 0. No skips or warnings. Covers strict historical features, half-open targets, future-mutation invariance, matured labels, calibration overlap, model outputs, development-only selection, invoice deduplication/returns/conflicts/timestamp spans, incomplete invoices, top-K ties/denominators, undefined metrics, API validation, hidden future fields, history cutoff, CSV, absent/tampered artifacts and run-path rejection.

Windows sandbox denied pytest temporary directories even inside the project; approved execution outside that sandbox passed. This is an execution restriction, not a skipped application test. API tests use httpx ASGITransport directly to avoid a host Starlette TestClient deprecation.

## Real experiment and artifact recomputation

```powershell
$env:PYTHONPATH='src'
python -m reorderiq.cli prepare
python -m reorderiq.cli run
python -m reorderiq.cli verify
```

Final run: `20261029T092203635364Z-627414f3`. Official workbook normalized to 36,553 orders and 5,851 buyers. All 87 weekly snapshots built. Development chose gradient boosting before the final holdout was opened. Final evaluation covers 13 Mondays, 39,754 buyer-weeks and 3,874 unique buyers.

Independent verification passed for all 13 artifact hashes, frozen selection, rebuilt SQL populations, actual future-order labels, pre-cutoff features, reported macro metrics and shared targets across four candidates. Machine-readable evidence: artifact-check.json.

Three full experiments produced exactly identical prediction table values, including a fresh feature-cache path and later cached data. Parquet bytes differ for one cache/serialization path; the first and final files are byte-identical. These are recorded separately in reproducibility.json. No model hyperparameters were tuned after viewing final results. The final run captures source.zip and rejects a changing code fingerprint during execution.

## Browser and interface

Local server: `python -m reorderiq.cli serve --port 8010`.

```powershell
python scripts/browser_check.py
```

**12 named checks passed; zero JavaScript page errors.** Real data loads, outcomes reveal/reset, model/capacity changes, selected-buyer focus, search/empty recovery, hidden-outcome CSV export, evidence/source views, failed-request retry and no page-level overflow at 1440, 1024, 768 and 390px. Keyboard skip navigation works. Chart text has no inherited SVG stroke and renders at >=11px in desktop/mobile captures. Results and captures are in browser/.

Playwright subprocess pipes were denied inside the Windows sandbox; approved execution outside it passed. Existing Chromium was used. No new browser installation was needed on this machine.

Impeccable's context engine could not install outside the writable workspace. The explicit launcher-unavailable fallback was reported and project context was read directly. A fresh finish reviewer inspected the supplied captures and found one material chart-typography problem; it was fixed, recaptured and scored resolved. The final ship verdict covers that scored fix, not a fresh whole-surface certification. FORM seed, QUALITY BAR and approved comp provenance were unavailable. Design documentation and its schema-v2 sidecar were separately refreshed from the actual code.

## Static, packaging and reports

```powershell
python -m ruff check src tests scripts
python -m ruff format --check src tests scripts
node --check src/reorderiq/web/app.js
python -m pip wheel --no-deps --no-cache-dir --disable-pip-version-check --wheel-dir .local/wheels .
python scripts/profile_data.py
python scripts/export_figures.py
```

Wheel build passed: `reorderiq-0.1.0-py3-none-any.whl`, 111,091 bytes. Wheel SHA-256: `615616dc0ceb3ac343bf0037b06f6e32372d84ddcffdbf25010e31b3479f0508`. Source package, SQL, web client, fonts and font license are included. Raw data and run artifacts are excluded. An initial no-build-isolation command failed because global setuptools was absent; the normal isolated build fetched the declared build tool and succeeded without changing global packages.

Descriptive data profile and standalone PNG/SVG model-evidence figures were exported from actual data/artifacts. Figure generation is not model fitting or further tuning. The Windows/Linux GitHub workflow is supplied but has not run on GitHub. Current source was exercised locally; no claim of production hosting, current Udaan performance or causal outreach effect is made.
