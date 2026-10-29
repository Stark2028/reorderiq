#!/usr/bin/env bash
# Run as root on the inspected EC2 host, after extracting the deployment bundle.
set -euo pipefail
cd /opt/reorderiq/current
docker compose -f deploy/aws/compose.yaml config --quiet
docker compose -f deploy/aws/compose.yaml build > /opt/reorderiq/build.log 2>&1
docker compose -f deploy/aws/compose.yaml up -d
container=$(docker compose -f deploy/aws/compose.yaml ps -q app)
for attempt in $(seq 1 60); do
    state=$(docker inspect --format '{{.State.Health.Status}}' "$container")
    if [ "$state" = healthy ]; then break; fi
    if [ "$attempt" = 60 ]; then docker logs --tail 60 "$container"; exit 1; fi
    sleep 3
done
proxy=saga-agent-proxy-1
config=/opt/saga/deploy/aws/Caddyfile
mkdir -p /opt/reorderiq/backups
backup=/opt/reorderiq/backups/Caddyfile-$(date -u +%Y%m%dT%H%M%SZ)
cp "$config" "$backup"
candidate=$(mktemp /opt/reorderiq/Caddyfile.XXXXXX)
cp "$config" "$candidate"
if ! grep -q '^reorderiq.65.0.103.235.sslip.io {' "$candidate"; then
    cat >> "$candidate" <<'CADDY'

reorderiq.65.0.103.235.sslip.io {
    encode zstd gzip
    header {
        X-Content-Type-Options nosniff
        Referrer-Policy same-origin
        X-Frame-Options DENY
    }
    request_body {
        max_size 1MB
    }
    reverse_proxy reorderiq:8010
}
CADDY
fi
docker cp "$candidate" "$proxy":/tmp/reorderiq-Caddyfile
docker exec "$proxy" caddy validate --config /tmp/reorderiq-Caddyfile --adapter caddyfile
# Preserve the bind-mounted inode so the existing proxy sees the new contents.
cat "$candidate" > "$config"
if ! docker exec "$proxy" caddy reload --config /etc/caddy/Caddyfile --adapter caddyfile; then
    cat "$backup" > "$config"
    docker exec "$proxy" caddy reload --config /etc/caddy/Caddyfile --adapter caddyfile
    exit 1
fi
echo 'ReorderIQ healthy; HTTPS route activated. Existing proxy routes preserved.'
