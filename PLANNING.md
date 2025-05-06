# 🎧 Top Songs Dashboard - Project Planning

## 📋 Project Overview

The Top Songs Dashboard is a learning-focused, end-to-end data engineering and analytics platform that simulates and processes real-time user song play data. The dashboard displays the **Top 10 songs** for each **region**, updated **hourly** and **daily**.

## 🏗️ Architecture

The system is composed of microservices and batch/streaming components:

```
[Simulated Clients] → [FastAPI Web Server] → [Kafka] → [Apache Spark Structured Streaming] → [MinIO (S3-compatible)]
                                                                                                     │
                                                                                                     ├─────────────┬─────────────┐
                                                                                                     ▼                           ▼
                                                                                               [ETL Jobs via Prefect]   [Aggregation Jobs via Prefect]
                                                                                                     │                           │
                                                                                                     ▼                           ▼
                                                                                               [Enriched Data in S3]   [Top N Songs in PostgreSQL]
                                                                                                                                 │
                                                                                                                                 ▼
                                                                                                                      [ReactJS Dashboard App]
```

## 🔧 Tech Stack

| Layer               | Technology                             |
|--------------------|-----------------------------------------|
| Data Simulation     | Python + OpenAI API                     |
| API Server          | FastAPI                                 |
| Messaging Queue     | Apache Kafka                            |
| Streaming Processor | Apache Spark Structured Streaming       |
| Object Storage      | MinIO (S3-compatible)                   |
| Workflow Orchestration | Prefect                             |
| Serving DB          | PostgreSQL                              |
| Dashboard Frontend  | ReactJS + Chart.js                      |
| Containerization    | Docker + Docker Compose                 |
| Python Package Mgmt | `uv` (for virtualenv + dependency mgmt) |

## 🔄 Data Flow

1. **Simulated clients** send song play events with metadata via REST API
2. **FastAPI server** pushes events to **Kafka**
3. **Spark** reads events from Kafka, processes them, and writes to **MinIO** in partitioned Parquet files
4. **Prefect** runs:
   - Enrichment jobs to add metadata
   - Aggregation jobs to calculate top songs
   - Loading jobs to update PostgreSQL
5. **ReactJS Dashboard** queries PostgreSQL and renders top 10 songs per region/hour/day

## 📁 Project Structure

```
top_songs_dashboard/
├── .gitignore                  # Git ignore rules
├── .python-version             # Python version lock (for pyenv or uv)
├── pyproject.toml              # Dependency and build configuration using uv
├── README.md                   # Project overview and usage
├── PLANNING.md                 # Project architecture, goals, and structure
├── TASK.md                     # Task tracking and progress
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
│   │   └── flows/              # Prefect flows for data pipelines
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

## 🧪 Development Setup

- All services containerized with **Docker**
- Single `docker-compose.yaml` file for local orchestration
- MinIO replaces AWS S3 with no code changes
- Python dependencies managed via **uv**

## 📚 Coding Style & Conventions

- **Language**: Python is the primary backend language
- **Style**: Follow PEP8
- **Type Hints**: Use Python type hints for all functions
- **Formatting**: Code should be formatted with `black`
- **Data Validation**: Use `pydantic` for data validation
- **APIs**: Use `FastAPI` for APIs
- **ORM**: Use `SQLAlchemy` or `SQLModel` if applicable
- **Documentation**: Write Google-style docstrings for every function
- **Code Organization**: Maintain modularity and single responsibility principle
- **File Size**: No file should exceed 500 lines of code

## 🧠 Project Goals

- Gain hands-on experience with distributed systems (Kafka, Spark)
- Explore real-time streaming architectures
- Practice data orchestration and analytics pipelines
- Design a robust and observable system
- Build a professional-grade data product with modularity and maintainability

## 🚀 Future Enhancements

- Add Redis caching for low-latency dashboard
- Add Prometheus + Grafana for observability
- Add user authentication (e.g., Auth0 or Firebase)
- Deploy on k8s (minikube or kind) for CI/CD training 