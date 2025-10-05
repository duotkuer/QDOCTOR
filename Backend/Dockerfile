# syntax=docker/dockerfile:1

FROM python:3.11-slim AS base
WORKDIR /app

# Builder stage: install dependencies in a venv
FROM base AS builder

# Install system dependencies required by pdfplumber and PyPDF2
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libffi-dev \
    libxml2-dev \
    libxslt1-dev \
    libjpeg-dev \
    zlib1g-dev \
    poppler-utils \
    && rm -rf /var/lib/apt/lists/*

# Create virtual environment
RUN python -m venv /app/.venv

# Copy requirements.txt and install Python dependencies
COPY --link requirements.txt ./
ENV PIP_CACHE_DIR=/root/.cache/pip
RUN --mount=type=cache,target=$PIP_CACHE_DIR \
    /app/.venv/bin/pip install --upgrade pip && \
    /app/.venv/bin/pip install --no-warn-script-location -r requirements.txt

# Copy application code (excluding .env, .git, .venv, etc.)
COPY --link . .

# Final stage: runtime image
FROM base AS final

# Create non-root user
RUN useradd -m appuser
USER appuser

WORKDIR /app

# Copy virtual environment from builder
COPY --from=builder /app/.venv /app/.venv

# Copy application code from builder
COPY --from=builder /app /app

ENV PATH="/app/.venv/bin:$PATH"

# Expose port for FastAPI (default: 8000)
EXPOSE 8000

# Entrypoint: run the FastAPI app with uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
