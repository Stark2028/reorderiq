# Public AWS deployment — 2026-10-29

Live app: https://reorderiq.65.0.103.235.sslip.io

## Deployment record

- Existing EC2 host in ap-south-1; no additional instance, load balancer, public port or database provisioned. Original SagaAgent app and proxy containers remain running.
- ReorderIQ image `reorderiq:a1f450c8`, container `reorderiq-app-1`, release `/opt/reorderiq/releases/a1f450c8`.
- Transport bundle SHA-256: `a1f450c84dc6e098dc0a61277084befa93f2767920ecc7f4862a9419fb443be6`; remote checksum passed before extraction.
- Runtime source corresponds to deployment-source commit `10648bd`. Activation-script B016 correction was subsequently applied to both the source checkout and host release; application code and frozen experiment were unchanged.
- Pinned run: `20261029T092203635364Z-627414f3`. All 13 manifest artifacts were verified; all 13 weekly populations, 39,754 buyer-weeks, historical features, actual order labels and four candidates' metrics were independently rebuilt inside the deployed container.
- Non-root UID/GID 10001, read-only root filesystem and artifact mount, dropped capabilities, 640 MiB/0.75 CPU limits, bounded logs and readiness-aware Docker health check. Measured memory after verification: 271.8 MiB. `pip check`: no broken requirements.

## Public verification

- Standard validated HTTPS requests returned HTTP 200 for readiness and metadata, with the correct pinned run. No insecure TLS bypass was used.
- `python scripts/browser_check.py --url https://reorderiq.65.0.103.235.sslip.io --output .local/deployment-browser`: all twelve browser flows passed, zero JavaScript errors. [Machine-readable checks](deployment-browser-results.json). Captures remain in the ignored local output directory; the original refinement screenshots are unchanged.
- Browser checks include real hidden-outcome data, date/reveal resets, model/capacity changes, current buyer details, empty/retry states, stale-export prevention, real CSV download, evidence/source navigation, keyboard charts, mobile focus/paging, dark theme and reduced motion.
- SagaAgent's existing HTTPS route retained its expected login redirect (303); following it returned HTTP 200. No SagaAgent container restart or data change was required.
- Local Python suite: 42 passed with warnings-as-errors. Ruff passed. Hosted deployment-source CI passed on Windows, Linux and frontend: https://github.com/Stark2028/reorderiq/actions/runs/40883687259.

Initial proxy-mount and browser-harness failures were corrected and rerun; see B016/B017 in BUGS.md. Read [the runbook](../deploy/aws/README.md) before redeploying or rolling back. This public historical-data portfolio demo shares a host and proxy with SagaAgent; public-IP stability, host availability and ongoing AWS usage charges remain limitations.
