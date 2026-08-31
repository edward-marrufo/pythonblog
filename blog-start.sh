#!/bin/bash

set -euo pipefail

COMPOSE_FILE="/opt/blog/docker-compose.prd.yaml"

export DB_PASSWORD="$(
    gcloud secrets versions access latest \
        --secret="db_password"
)"

exec /bin/podman-compose \
    -f "$COMPOSE_FILE" \
    up -d

unset DB_PASSWORD