# 🎧 Top Songs Dashboard - Project Description

## 🧠 Overview

This project is a learning-focused, end-to-end data engineering and analytics platform that simulates and processes real-time user song play data. The final output is a web dashboard that displays the **Top 10 songs** for each **region**, updated **hourly** and **daily**. The stack involves streaming data pipelines, data lake storage, enrichment processes, and modern dashboard rendering.

The project is designed to be modular, containerized using Docker, and uses `uv` for Python package management.

---

## 🎯 Objectives

- Simulate real-time song play data with metadata using LLM-generated inputs.
- Ingest and stream data via a REST API into Kafka.
- Use Apache Spark to process streaming data and store it in MinIO (S3-compatible).
- Enrich and aggregate data via Airflow-managed pipelines.
- Persist the final top-song statistics into PostgreSQL for querying.
- Serve this data via a frontend dashboard built in ReactJS.

---

## 🔧 Tech Stack

| Layer               | Technology                             |
|--------------------|-----------------------------------------|
| Data Simulation     | Python + OpenAI API                     |
| API Server          | FastAPI                                 |
| Messaging Queue     | Apache Kafka                            |
| Streaming Processor | Apache Spark Structured Streaming       |
| Object Storage      | MinIO (S3-compatible)                   |
| Workflow Orchestration | Apache Airflow                      |
| Serving DB          | PostgreSQL                              |
| Dashboard Frontend  | ReactJS + Chart.js                      |
| Containerization    | Docker + Docker Compose                 |
| Python Package Mgmt | `uv` (for virtualenv + dependency mgmt) |

---

## 🔄 Data Flow (High-Level)

1. **Simulated clients** send song play events with metadata via REST API.
2. **FastAPI server** pushes events to **Kafka**.
3. **Spark** reads events from Kafka, processes them, and writes to **MinIO** in partitioned Parquet files.
4. **Airflow** runs:
   - Enrichment jobs to add metadata
   - Aggregation jobs to calculate top songs
   - Loading jobs to update PostgreSQL
5. **ReactJS Dashboard** queries PostgreSQL and renders top 10 songs per region/hour/day.

---

## 📦 Deliverables

- Dockerized microservices for ingestion, processing, and frontend
- Airflow DAGs for data orchestration
- Clean, testable Python code using `uv`
- React-based web dashboard
- Example simulated data and usage instructions
- Deployment-ready `docker-compose.yaml`

---

## 🚀 Project Goals

- Gain hands-on experience with distributed systems (Kafka, Spark)
- Explore real-time streaming architectures
- Practice data orchestration and analytics pipelines
- Design a robust and observable system
- Build a professional-grade data product with modularity and maintainability

---

## 📁 Repository Structure (Tentative)

```css
top_songs_dashboard/
├── .gitignore                  # Git ignore rules
├── .python-version             # Python version lock (for pyenv or uv)
├── pyproject.toml              # Dependency and build configuration using uv
├── README.md                   # Project overview and usage
├── docker/                     # Dockerfiles and container build setup
├── docs/                       # Project documentation, plans, and diagrams

├── top_songs/                  # Main application Python package
│
│   ├── cli/                    # CLI commands (e.g., Typer/Click-based interfaces)
│
│   ├── core/                   # Core shared logic across domains
│   │   ├── config/             # App settings, environment loader, global config
│   │   ├── models/             # Shared domain models and schemas
│   │   └── utils/              # Reusable utilities (logging, validation, etc.)
│
│   ├── ingestion/              # Ingestion layer for incoming data
│   │   ├── api/                # FastAPI service for receiving event data
│   │   └── simulator/          # Simulated client that generates song play events
│
│   ├── orchestration/          # Workflow orchestration logic
│   │   └── dags/               # Airflow DAGs or other orchestrated pipelines
│
│   ├── processing/             # Data processing jobs
│   │   ├── enrichment/         # Metadata enhancement, lookups, etc.
│   │   └── streaming/          # Real-time processing jobs (e.g., Spark, Kafka)
│
│   ├── serving/                # Data serving layer
│   │   ├── api/                # Optional API layer for exposing processed data
│   │   └── dashboard/          # React frontend for visualizing top songs
│
│   └── storage/                # Data persistence and storage layer
│       ├── database/           # PostgreSQL-related logic (schemas, access)
│       └── object_store/       # S3/MinIO integration for data lake storage
```

---

