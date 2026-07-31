#!/bin/bash
# scripts/docker-down.sh

set -e

echo "🛑 Stopping Agentic RAG Assistant..."

cd infra/docker
docker-compose down

echo ""
echo "✅ All services stopped"
echo ""
echo "💾 Data volumes preserved. To delete data:"
echo "   docker-compose down -v"