FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

# Install curl for Docker healthcheck and minimal utilities
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy dependency specifications first to leverage Docker layer caching
COPY pyproject.toml .
RUN pip install --upgrade pip

# Copy source code, migrations and alembic configuration
COPY src/ ./src
COPY migrations/ ./migrations
COPY alembic.ini .

# Install package and CLI entry points (politiklar-api, politiklar-crawl)
RUN pip install -e .

# Prepare persistent source archive location
RUN mkdir -p /var/lib/politiklar/source-archive

EXPOSE 8000

# Default command starts the API service
CMD ["politiklar-api", "--host", "0.0.0.0", "--port", "8000"]
