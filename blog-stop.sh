#!/bin/bash

set -euo pipefail

COMPOSE_FAIL="/opt/blog/docker-compose.prd.yaml"

exec /bin/podman-compose \
    -f "$COMPOSE_FILE" \
    down