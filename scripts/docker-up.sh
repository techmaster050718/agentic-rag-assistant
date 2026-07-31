#!/bin/bash
echo "Starting Agentic RAG Document Assistant via Docker Compose..."
docker-compose -f infra/docker/docker-compose.yml up -d
echo "✅ Services started. Access frontend at http://localhost:3000"
