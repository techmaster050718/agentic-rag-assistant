FROM python:3.11-slim

WORKDIR /app

# FORCE DOCKER CACHE BUST (Change this value to invalidate cache)
ENV CACHE_BUSTER=20260817_V3_NUCLEAR

# System deps:
# - build-essential: C compiler for asyncpg, pydantic, etc.
# - libpq-dev: PostgreSQL client headers for asyncpg
# - curl: healthcheck utility
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies first (layer cache optimisation)
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy application code (Ab yeh 100% naya code copy karega)
COPY . .

# Expose port (Render injects $PORT at runtime)
EXPOSE 8000

# Start server — $PORT is set by Render; fallback to 8000 for local
CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}"]