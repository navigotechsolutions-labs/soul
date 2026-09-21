# Production Dockerfile for Soul Engine REST API
FROM python:3.11-slim

WORKDIR /app

# Install build essentials
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy dependency specifications
COPY pyproject.toml README.md ./

# Install Soul Engine and API dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir "fastapi>=0.100.0" "uvicorn>=0.20.0"

# Copy application source code
COPY soul/ ./soul/
COPY serve.py app.py ./

# Install package in editable mode
RUN pip install --no-cache-dir -e .

# Expose API port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')" || exit 1

# Start the API server
CMD ["python", "serve.py", "--host", "0.0.0.0", "--port", "8000"]
