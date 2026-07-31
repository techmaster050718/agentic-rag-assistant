#!/bin/bash
# scripts/docker-logs.sh

set -e

SERVICE=${1:-}

cd infra/docker

if [ -z "$SERVICE" ]; then
    echo "📋 Showing logs for all services..."
    docker-compose logs -f
else
    echo "📋 Showing logs for $SERVICE..."
    docker-compose logs -f $SERVICE
fi