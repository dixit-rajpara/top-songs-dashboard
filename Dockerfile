FROM python:3.12-slim

# Set environment variables for Python and uv
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    UV_LINK_MODE=copy \
    UV_COMPILE_BYTECODE=1 \
    UV_PYTHON_DOWNLOADS=never

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential curl ca-certificates \
    libpq-dev pkg-config librdkafka-dev \
    && rm -rf /var/lib/apt/lists/*

# Install uv package manager (from official image)
COPY --from=ghcr.io/astral-sh/uv:0.6.8 /uv /uvx /bin/

# Use /py for dependency install context
WORKDIR /py
COPY pyproject.toml ./
COPY uv.lock ./

RUN uv sync --frozen --no-dev --no-install-project && \
    apt-get purge -y --auto-remove -o APT::AutoRemove::RecommendsImportant=false build-essential

# Set up application code
WORKDIR /app
COPY top_songs /app/top_songs
COPY scripts/run.sh /scripts/run.sh

ENV PATH="/scripts:/py/.venv/bin:$PATH"

# Expose FastAPI default port
EXPOSE 8000

# Healthcheck (simple HTTP GET)
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
  CMD curl --fail http://localhost:8000/health || exit 1

# Default: run the entrypoint script
CMD ["run.sh"]

# For production, you may use gunicorn with uvicorn workers:
# CMD ["gunicorn", "-k", "uvicorn.workers.UvicornWorker", "top_songs.ingestion.api.app:create_app", "--bind", "0.0.0.0:8000"] 