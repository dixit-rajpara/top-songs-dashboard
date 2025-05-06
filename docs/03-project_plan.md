# 🗓️ Top Songs Dashboard - Detailed Project Plan

This plan outlines the phases, tasks, and deliverables required to implement the complete Top Songs Dashboard project. Each phase is organized with dependencies and recommended timelines to help you stay on track.

---

## 🚦 Phase 0: Project Setup (1 Day)

### ✅ Goals
- Establish base repo, environments, and dev tools

### 🔧 Tasks
- [ ] Initialize Git repository and folder structure
- [ ] Set up `uv` environment and `.uv` config
- [ ] Create `docker-compose.yaml` for all services
- [ ] Add MinIO container and test connectivity
- [ ] Define global `.env` config (hostnames, ports, keys)

### 📦 Deliverables
- Working local dev setup with MinIO
- Repo skeleton committed

---

## 🎮 Phase 1: Simulated Clients & API Server (2–3 Days)

### ✅ Goals
- Generate realistic song play data and ingest it via FastAPI

### 🔧 Tasks
- [ ] Write LLM-based song play data generator (with location, user ID, timestamp, etc.)
- [ ] Create FastAPI server with `POST /play` endpoint
- [ ] Integrate Kafka producer in API server
- [ ] Dockerize the API server
- [ ] Use `uvicorn` + `gunicorn` for production-like setup

### 📦 Deliverables
- Simulated clients sending events to REST API
- Kafka receives and stores events in topic `song-plays`

---

## 🔄 Phase 2: Kafka to MinIO via Spark (3–4 Days)

### ✅ Goals
- Stream song events from Kafka and persist raw data in MinIO as Parquet

### 🔧 Tasks
- [ ] Set up Kafka container in Docker Compose
- [ ] Write a Spark Structured Streaming job (Kafka → Parquet)
- [ ] Partition output by `region/date/hour`
- [ ] Configure MinIO access via `fs.s3a` in Spark
- [ ] Dockerize the Spark job with configs

### 📦 Deliverables
- Hourly Parquet files in MinIO, partitioned by region and time
- Logs + checkpointing for reliable ingestion

---

## 🛠️ Phase 3: Airflow for ETL & Aggregation (4–5 Days)

### ✅ Goals
- Orchestrate enrichment and aggregation jobs using Airflow DAGs

### 🔧 Tasks
- [ ] Set up Airflow with Docker Compose
- [ ] Create DAG: read raw parquet, enrich data, write enriched parquet
- [ ] Create DAG: run top-10 aggregation and update PostgreSQL
- [ ] Define schemas: `top_songs_hourly`, `top_songs_daily`
- [ ] Use `psycopg2` or `SQLAlchemy` to push aggregates to DB

### 📦 Deliverables
- Automated ETL and aggregation via DAGs
- Top N tables in PostgreSQL updated hourly/daily

---

## 🌐 Phase 4: Frontend Dashboard (3 Days)

### ✅ Goals
- Build ReactJS-based UI to visualize top songs

### 🔧 Tasks
- [ ] Scaffold dashboard with Create React App / Vite
- [ ] Implement views: region/hour/day selector
- [ ] Fetch data from API (e.g., FastAPI or Node layer)
- [ ] Integrate charting library (Chart.js or Recharts)
- [ ] Style with minimal CSS or Tailwind

### 📦 Deliverables
- Interactive dashboard showing Top 10 songs by region/time
- API integration tested locally

---

## 🧪 Phase 5: Final Testing & Polish (1–2 Days)

### ✅ Goals
- Ensure stability and reproducibility

### 🔧 Tasks
- [ ] Write sample test suite for API + pipelines
- [ ] Add error handling and logging in services
- [ ] Clean up Docker volumes, env configs
- [ ] Document usage in `README.md`

### 📦 Deliverables
- Fully functional, reproducible local stack
- Docs for running and extending the project

---

## ⏱️ Total Estimated Timeline: **2 to 2.5 Weeks**

| Phase            | Estimated Duration |
|------------------|--------------------|
| Setup            | 1 day              |
| Clients & API    | 2–3 days           |
| Kafka to S3      | 3–4 days           |
| Airflow Pipelines| 4–5 days           |
| Frontend         | 3 days             |
| Final Polish     | 1–2 days           |

---

## 📌 Notes

- Tasks are modular and can be parallelized where possible
- Spark jobs and DAGs can be iterated incrementally
- Time estimates assume ~4–5 focused hours/day


