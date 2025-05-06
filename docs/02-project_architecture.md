# 🏗️ Top Songs Dashboard - Architecture Document

## 📐 Overview

This document describes the architecture for the **Top Songs Dashboard** project. The system is composed of microservices and batch/streaming components for ingesting, processing, enriching, and serving analytics over simulated song play data. It is designed for modularity, scalability, and local development using Docker and MinIO.

---

## 🔄 High-Level Workflow

```css
[Simulated Clients]
         │
         ▼
[FastAPI Web Server]
         │
         ▼
      [Kafka]
         │
         ▼
[Apache Spark Structured Streaming]
         │
         ▼
  [MinIO (S3-compatible)]
         │
         ├────────────┬────────────┐
         ▼                         ▼
[ETL Jobs via Airflow]     [Aggregation Jobs via Airflow]
         │                         │
         ▼                         ▼
[Enriched Data in S3]     [Top N Songs in PostgreSQL]
                                   │
                                   ▼
                        [ReactJS Dashboard App]

```

---

## 🧱 Component Breakdown

### 1. **Simulated Clients**
- **Role**: Emulates song plays from users across different regions using LLM-generated data.
- **Tools**: Python, asyncio, OpenAI API, `requests`
- **Behavior**: Sends JSON payloads to the REST API endpoint at a configurable frequency.

---

### 2. **API Server (FastAPI)**
- **Role**: Receives song play events and publishes them to Kafka.
- **Tools**: FastAPI, kafka-python / confluent-kafka
- **Endpoints**:
  - `POST /play`: Accepts a song play with metadata.
- **Deployment**: Docker container with health and metrics endpoints.

---

### 3. **Apache Kafka**
- **Role**: Decouples event producers and consumers, buffers high-throughput data.
- **Topic Structure**: One topic for all plays (e.g., `song-plays`), or partitioned by region/time.
- **Config**: Runs locally via Docker Compose.

---

### 4. **Spark Streaming Job**
- **Role**: Reads from Kafka and writes raw data to MinIO in hourly/daily partitions.
- **Output Format**: Parquet
- **Partitioning**: By region and date (`/region=US/date=2025-04-23/hour=14`)
- **Tech**: Spark Structured Streaming, `fs.s3a` to MinIO, Dockerized Spark worker

---

### 5. **MinIO**
- **Role**: Local S3-compatible object storage for raw and enriched data.
- **Interface**: S3-compatible, used by Spark, Airflow, etc.
- **Deployment**: Standalone or Docker container

---

### 6. **Apache Airflow**
- **Role**: Orchestrates data pipelines including:
  - ETL/ELT from MinIO
  - Metadata enrichment
  - Aggregation (e.g., Top 10 songs)
  - Load to PostgreSQL
- **DAGs**: Scheduled to run hourly/daily
- **Deployment**: Docker-based Airflow setup with local executor or Celery

---

### 7. **PostgreSQL**
- **Role**: Serves the top song analytics data to the dashboard.
- **Tables**:
  - `top_songs_hourly(region, timestamp, song, plays)`
  - `top_songs_daily(region, date, song, plays)`
- **Access**: Queried by dashboard via REST API or GraphQL

---

### 8. **ReactJS Dashboard**
- **Role**: Frontend app showing top 10 songs for each region/day/hour.
- **Tech**: ReactJS, Axios, Chart.js or Recharts
- **Features**:
  - Region/time selector
  - Dynamic charts
  - Polling or refresh mechanism

---

## ⚙️ System Characteristics

| Property         | Approach                                      |
|------------------|-----------------------------------------------|
| **Scalability**  | Kafka + Spark can scale horizontally          |
| **Modularity**   | Each service runs independently in Docker     |
| **Observability**| Prometheus-compatible metrics (later stage)   |
| **Cost-effective** | All components run locally without cloud costs |
| **Resilience**   | Kafka buffering + checkpointed Spark jobs     |

---

## 🧪 Dev & Deployment Setup

- All services containerized with **Docker**
- Single `docker-compose.yaml` file for local orchestration
- MinIO replaces AWS S3 with no code changes
- Python dependencies managed via **uv**

---

## 📌 Future Enhancements

- Add Redis caching for low-latency dashboard
- Add Prometheus + Grafana for observability
- Add user authentication (e.g., Auth0 or Firebase)
- Deploy on k8s (minikube or kind) for CI/CD training


