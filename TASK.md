# 🎧 Top Songs Dashboard - Tasks

## 🚦 Phase 0: Project Setup
- [ ] Initialize Git repository and folder structure
- [ ] Set up `uv` environment and `.uv` config
- [ ] Create `docker-compose.yaml` for all services
- [ ] Add MinIO container and test connectivity
- [ ] Define global `.env` config (hostnames, ports, keys)

## 🎮 Phase 1: Simulated Clients & API Server
- [ ] Write LLM-based song play data generator (with location, user ID, timestamp, etc.)
- [ ] Create FastAPI server with `POST /play` endpoint
- [ ] Integrate Kafka producer in API server
- [ ] Dockerize the API server
- [ ] Use `uvicorn` + `gunicorn` for production-like setup

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
- [ ] Use `psycopg2` or `SQLAlchemy` to push aggregates to DB

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
*No tasks completed yet*

## 🔍 Discovered During Work
*New tasks discovered during development will be added here* 