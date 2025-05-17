# 🎧 Top Songs Dashboard

A learning-focused, end-to-end data engineering and analytics platform that simulates and processes real-time user song play data. The dashboard displays the **Top 10 songs** for each **region**, updated **hourly** and **daily**.

## 📋 Project Overview

The Top Songs Dashboard is an end-to-end data engineering project that demonstrates:

- Real-time data streaming and processing
- Data lake and data warehouse integration
- ETL/ELT pipelines and orchestration
- Analytics dashboard visualization

## 🔧 Tech Stack

- **Data Simulation**: Python + OpenAI API
- **API Server**: FastAPI
- **Messaging Queue**: Apache Kafka (confluent-kafka)
- **Streaming Processor**: Apache Spark Structured Streaming
- **Object Storage**: MinIO (S3-compatible) via boto3
- **Workflow Orchestration**: Prefect
- **Serving DB**: PostgreSQL with asyncpg
- **CLI Interface**: Typer + Rich
- **Dashboard Frontend**: ReactJS + Chart.js
- **Containerization**: Docker + Docker Compose
- **Python Package Mgmt**: `uv` (for virtualenv + dependency mgmt)

## 🚀 Getting Started

### Prerequisites

- Docker and Docker Compose
- Python 3.12+
- `uv` package manager
- OpenAI API key (for data simulation)

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/dixit-rajpara/top_songs_dashboard.git
   cd top_songs_dashboard
   ```

2. Set up the Python environment:
   ```bash
   uv venv
   uv pip install -e .
   ```

3. Create a `.env` file with configuration:
   ```
   OPENAI_API_KEY=your_api_key_here
   MINIO_ROOT_USER=minioadmin
   MINIO_ROOT_PASSWORD=minioadmin
   POSTGRES_USER=postgres
   POSTGRES_PASSWORD=postgres
   ```

4. Start the Docker services:
   ```bash
   docker-compose up -d
   ```

### Running the Application

1. Check connectivity to all services:
   ```bash
   top-songs check-connectivity
   ```

2. Start the data simulator:
   ```bash
   top-songs simulate generate-master --help
   top-songs simulate run --help
   ```

3. Access the dashboard:
   - Frontend: http://localhost:3000
   - Prefect UI: http://localhost:4200
   - MinIO Console: http://localhost:9001
   - Spark UI: http://localhost:4040

## 📄 Project Structure

```
top_songs_dashboard/
├── README.md                   # This file
├── PLANNING.md                 # Project architecture, goals, and structure
├── TASK.md                     # Task tracking and progress
├── docker/                     # Dockerfiles and container build setup
├── docs/                       # Project documentation, plans, and diagrams
├── top_songs/                  # Main application Python package
│   ├── cli/                    # CLI commands
│   ├── core/                   # Core shared logic
│   ├── storage/                # Database and object store interfaces
│   ├── streaming/              # Kafka and streaming interfaces
│   └── ...                     # Other modules
├── tests/                      # Unit and integration tests
```

For more details about the project structure, see [PLANNING.md](PLANNING.md).

## 🔄 Data Flow

1. **Simulated clients** send song play events with metadata via REST API
2. **FastAPI server** pushes events to **Kafka**
3. **Spark** reads events from Kafka, processes them, and writes to **MinIO**
4. **Prefect** orchestrates enrichment and aggregation jobs
5. **ReactJS Dashboard** queries PostgreSQL and renders top 10 songs

## 🧪 Development

### Creating a New Component

1. Follow the modular project structure in `top_songs/`
2. Add appropriate tests in `tests/`
3. Update documentation where relevant

### Interfaces

The project provides several high-level interfaces:
- **KafkaInterface**: For producing and consuming Kafka messages
- **PostgresInterface**: For PostgreSQL database operations
- **ObjectStoreInterface**: For MinIO/S3 object storage operations

### Running Tests

```bash
pytest
```

## 📚 Documentation

- See `docs/` directory for detailed documentation
- Check `PLANNING.md` for project architecture
- View `TASK.md` for current task status

## 🔗 Useful Links

- [Apache Kafka Documentation](https://kafka.apache.org/documentation/)
- [Apache Spark Documentation](https://spark.apache.org/docs/latest/)
- [Prefect Documentation](https://docs.prefect.io/)
- [MinIO Documentation](https://min.io/docs/minio/container/index.html)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Confluent-Kafka Python](https://docs.confluent.io/kafka-clients/python/current/overview.html)
- [Asyncpg Documentation](https://magicstack.github.io/asyncpg/current/)

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## Data Simulator CLI Usage

The data simulator is available as a subcommand of the main CLI:

### Generate Master Data

```
top-songs simulate generate-master [OPTIONS]
```

**Options:**
- `--output-dir TEXT`         Directory to store master data files. (Default: `data/master/`)
- `--num-songs INTEGER`       Number of song records to generate. (Default: 1000)
- `--num-users INTEGER`       Number of user records to generate. (Default: 5000)
- `--num-locations INTEGER`   Number of location/region records to generate. (Default: 100)
- `--format TEXT`             Output format for master data (`csv` or `json`). (Default: `csv`)

### Run Data Simulation

```
top-songs simulate run [OPTIONS]
```

**Options:**
- `--historical`              Enable historical mode.
- `--live`                    Enable live mode.
- `--start-datetime TEXT`     Start ISO datetime for historical data (required for historical).
- `--end-datetime TEXT`       End ISO datetime for historical data (required for historical).
- `--posting-rate FLOAT`      Max events per second to post to the API (historical mode). (Default: 10.0)
- `--duration-seconds INT`    Duration for live simulation in seconds (0 = indefinite). (Default: 0)
- `--master-data-dir TEXT`    Directory to load master data from. (Default: `data/master/`)
- `--volume INTEGER`          Total number of play events to generate (historical) or events per minute (live). (Default: 10000 for historical, 60 for live)
- `--threads INTEGER`         Number of parallel threads for generating/posting. (Default: 4)
- `--api-endpoint TEXT`       The URL of the API endpoint to post play events. (Default: `http://localhost:8000/play`)
- `--format TEXT`             Master data file format (`csv` or `json`). (Default: `csv`)

**Example:**

```
top-songs simulate generate-master --num-songs 100 --num-users 200 --num-locations 10 --format csv

top-songs simulate run --historical --start-datetime "2023-01-01T00:00:00" --end-datetime "2023-01-02T00:00:00" --volume 1000
```
