# 🎧 Top Songs Dashboard - Tasks

## 🚦 Phase 0: Project Setup
- [x] Initialize Git repository and folder structure
- [x] Set up `uv` environment and `.uv` config
- [ ] Create `docker-compose.yaml` for all services *(deferred: Kafka, MinIO, and Postgres are running as shared services on host; project-specific compose will be added later)*
- [x] Add MinIO container and test connectivity *(see above note)*
- [x] Define global `.env` config (hostnames, ports, keys)
- [x] Implement CLI command to check connectivity of all services (Postgres, Kafka, MinIO/S3, Prefect)
- [x] Implement core interfaces for storage (PostgreSQL, S3/MinIO)
- [x] Implement Kafka interface for streaming data

## 🎮 Phase 1: Simulated Clients & API Server
- [x] Write Faker/Simpy-based song play data generator (with location, user ID, timestamp, etc.)
- [x] Create FastAPI server with `POST /play` endpoint
- [x] Integrate Kafka producer in API server
- [x] Dockerize the API server
- [x] Use `uvicorn` + `gunicorn` for production-like setup
- [x] Add docker-compose.yaml for API server orchestration

## 🔄 Phase 2: Kafka to MinIO via Spark
- [ ] Set up Kafka container in Docker Compose
- [ ] Write a Spark Structured Streaming job (Kafka → Parquet)
- [ ] Partition output by `region/date/hour`
- [ ] Configure MinIO access via `fs.s3a` in Spark
- [ ] Dockerize the Spark job with configs

## 🛠️ Phase 3: Prefect for ETL & Aggregation
- [ ] Set up Prefect with Docker Compose
- [ ] Create Flow: read raw parquet, enrich data, write enriched parquet
- [ ] Create Flow: run top-10 aggregation and update PostgreSQL
- [ ] Define schemas: `top_songs_hourly`, `top_songs_daily`
- [ ] Use `asyncpg` to push aggregates to DB

## 🌐 Phase 4: Frontend Dashboard
- [ ] Scaffold dashboard with Create React App / Vite
- [ ] Implement views: region/hour/day selector
- [ ] Fetch data from API (e.g., FastAPI or Node layer)
- [ ] Integrate charting library (Chart.js or Recharts)
- [ ] Style with minimal CSS or Tailwind

## 🧪 Phase 5: Final Testing & Polish
- [ ] Write sample test suite for API + pipelines
- [ ] Add error handling and logging in services
- [ ] Clean up Docker volumes, env configs
- [ ] Document usage in `README.md`
- [ ] Add unit tests for CLI commands (connectivity check, etc.)
- [ ] Add unit tests for storage and streaming interfaces

## ⏰ Timeline Overview
| Phase            | Estimated Duration |
|------------------|--------------------|
| Setup            | 1 day              |
| Clients & API    | 2–3 days           |
| Kafka to S3      | 3–4 days           |
| Prefect Pipelines| 4–5 days           |
| Frontend         | 3 days             |
| Final Polish     | 1–2 days           |

## 📋 Completed Tasks
- [x] Initialize Git repository and folder structure
- [x] Set up `uv` environment and `.uv` config
- [x] Define global `.env` config (hostnames, ports, keys)
- [x] Implement CLI command to check connectivity of all services (Postgres, Kafka, MinIO/S3, Prefect)
- [x] Implement core interfaces for storage (PostgreSQL, S3/MinIO)
- [x] Implement Kafka interface for streaming data

## 🔍 Discovered During Work
- Kafka, MinIO, and Postgres are running as shared containers on the host for multiple projects. Project-specific `docker-compose.yaml` will be created later to orchestrate all services together for this project.
- Need to add unit tests for CLI commands (connectivity check, etc.)
- Need to add unit tests for storage and streaming interfaces
- Moved connectivity check business logic from CLI to core module
- Dockerfile for API server added; supports both uvicorn and gunicorn entrypoints for production flexibility.
- docker-compose.yaml is structured for easy extension with Kafka, MinIO, Postgres, etc. in future phases.

*New tasks discovered during development will be added here* 