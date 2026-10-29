# ReorderIQ on the existing EC2 host

The app runs as a separate non-root, read-only Docker container, limited to 640 MiB and 0.75 CPU. It serves the committed React build and an immutable, independently verified experiment. No training, pickle loading, public database or extra public port is required. Caddy provides HTTPS on `reorderiq.65.0.103.235.sslip.io`; the original SagaAgent route remains intact.

## Package and activate

From an installed Python 3.12 project environment, run `python scripts/build_deployment.py`. Alternatively set `PYTHONPATH=src` when running from the checkout. This verifies all original artifact hashes, rebuilt populations/features/labels and metrics before creating `.local/deployment.tar.gz`. The bundle includes the current application and the selected completed experiment. Keep the bundle private; raw downloads and local credentials are never included.

Transfer the bundle using a private S3 object and a short-lived presigned download URL. The existing source bucket has a seven-day expiration policy, so it is transport storage only. Persistent serving artifacts live under `/opt/reorderiq/releases/<revision>/artifacts` on the EC2 disk. Preserve the local original run separately. Never write a presigned URL into Git or public logs.

Extract into a new `/opt/reorderiq/releases/<revision>` directory, verify the transferred bundle SHA-256, and point `/opt/reorderiq/current` at that release. Set `REORDERIQ_REVISION=<revision>`, then execute `bash /opt/reorderiq/current/deploy/aws/activate.sh` through AWS Systems Manager. The existing Docker network `saga-agent_default` and proxy `saga-agent-proxy-1` must exist; this configuration intentionally does not create another server or proxy.

The activation script builds the image, waits for artifact-aware container health, backs up the existing proxy config, validates an appended hostname route and gracefully reloads Caddy. A failed reload restores the saved proxy config. Build logs live in `/opt/reorderiq/build.log`. See [Caddy reload documentation](https://caddyserver.com/docs/command-line) and [AWS Run Command](https://docs.aws.amazon.com/us_en/systems-manager/latest/userguide/run-command.html).

## Check and maintain

- `https://reorderiq.65.0.103.235.sslip.io/api/status` must report `ready: true` and the pinned run ID.
- Run `python scripts/browser_check.py --url https://reorderiq.65.0.103.235.sslip.io --output .local/deployment-browser` against the real public application.
- Check that the SagaAgent HTTPS route still responds.
- Inspect `docker compose -f deploy/aws/compose.yaml ps` from the current release and Docker logs when diagnosing failures.
- Updating the GitHub repository does not automatically deploy. Repeat verified bundling and activation deliberately.

## Rollback and limits

Keep the prior release, image and proxy backup. To roll back the application, restore the previous `current` symlink, set its recorded `REORDERIQ_REVISION`, and run `docker compose -f deploy/aws/compose.yaml up -d --no-build` from that release. To undo only the new route, copy the recorded pre-change Caddyfile contents into `/opt/saga/deploy/aws/Caddyfile` (preserve the bind-mounted inode), validate and reload the proxy. Never delete SagaAgent volumes or run its Compose `down` command.

The demonstration is publicly readable historical UCI evidence, without accounts or private retailer records. Outcome reveal is educational, not access control. The hostname depends on this host retaining its public IP, and both applications share one host and reverse proxy. Existing EC2 charges continue; artifact transfer/storage can add usage charges. No extra EC2 instance, load balancer, paid domain or managed database is provisioned. This is portfolio hosting, not a highly available production service.
