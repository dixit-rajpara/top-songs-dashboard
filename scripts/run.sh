#!/bin/sh
set -e

# Optional: Run migrations here if needed
# echo "Running migrations..."
# uv run alembic upgrade head

MODE=${APP_ENV:-prod}

if [ "$MODE" = "dev" ]; then
  echo "Starting API server in development mode (uvicorn, reload)..."
  exec uvicorn top_songs.ingestion.api.app:create_app --factory --host 0.0.0.0 --port 8000 --reload
else
  echo "Starting API server in production mode (gunicorn + uvicorn workers)..."
  exec gunicorn -k uvicorn.workers.UvicornWorker top_songs.ingestion.api.app:create_app --bind 0.0.0.0:8000 --workers 4
fi 