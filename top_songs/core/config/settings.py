from typing import Optional
from pydantic import PostgresDsn
from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path


class KafkaSettings(BaseSettings):
    """Kafka connection settings."""
    bootstrap_servers: str = "localhost:9092"
    topic_name: str = "song-plays"


class MinioSettings(BaseSettings):
    """MinIO (S3-compatible) storage settings."""
    endpoint: str = "localhost:9000"
    access_key: str
    secret_key: str
    secure: bool = False
    bucket_name: str = "song-data"
    region: str = "us-east-1"


class PostgresSettings(BaseSettings):
    """PostgreSQL database settings."""
    # When direct initialization is used in tests, use postgres_dsn
    # But also allow postgres_dsn and database_url as aliases for env vars
    postgres_dsn: PostgresDsn
    min_connections: int = 1
    max_connections: int = 10
    
    model_config = SettingsConfigDict(
        # Allow aliases when loading from environment variables
        env_mapping={
            "postgres_dsn": ["dsn", "database_url"],
        }
    )


class ApiSettings(BaseSettings):
    """API server settings."""
    host: str = "0.0.0.0"
    port: int = 8000
    debug: bool = False
    workers: int = 4


class SparkSettings(BaseSettings):
    """Apache Spark configuration settings."""
    master: str = "local[*]"
    app_name: str = "TopSongsDashboard"
    checkpoint_location: str = "/tmp/checkpoint"
    batch_interval_seconds: int = 60


class PrefectSettings(BaseSettings):
    """Prefect workflow orchestration settings."""
    api_url: str = "http://localhost:4200/api"
    ui_port: int = 4200
    agent_queue_name: str = "default"
    flow_storage_path: str = "./storage/prefect"


class Settings(BaseSettings):
    """Main application settings."""
    model_config = SettingsConfigDict(
        env_file=".env.dev",
        env_file_encoding="utf-8",
        env_nested_delimiter="__",
        case_sensitive=False,
    )

    # General settings
    environment: str = "development"
    debug: bool = True
    project_name: str = "Top Songs Dashboard"
    
    # Logging settings
    logs_dir: str = "logs"  # Can be relative or absolute path
    log_output: str = "both"  # Options: "file", "console", "both"
    
    # Component settings
    kafka: KafkaSettings = KafkaSettings()
    minio: Optional[MinioSettings] = None
    postgres: Optional[PostgresSettings] = None
    api: ApiSettings = ApiSettings()
    spark: SparkSettings = SparkSettings()
    prefect: PrefectSettings = PrefectSettings()

    @property
    def project_root(self) -> Path:
        """
        Returns the absolute path to the project root directory.
        """
        return Path(__file__).resolve().parent.parent.parent.parent

    @property
    def logs_path(self) -> Path:
        """
        Returns the absolute path to the logs directory.
        If logs_dir is an absolute path, returns it as is.
        If logs_dir is a relative path, resolves it relative to project_root.
        """
        logs_dir_path = Path(self.logs_dir)
        if logs_dir_path.is_absolute():
            return logs_dir_path
        return self.project_root / self.logs_dir

    def __init__(self, **data):
        """Initialize settings, attempting to create nested settings if possible."""
        super().__init__(**data)
        
        # Try to initialize MinioSettings if environment variables are available
        try:
            if self.minio is None:
                self.minio = MinioSettings()
        except Exception:
            # Keep as None if validation fails
            pass
            
        # Try to initialize PostgresSettings if environment variables are available
        try:
            if self.postgres is None:
                self.postgres = PostgresSettings()
        except Exception:
            # Keep as None if validation fails
            pass


# Create a settings instance that can be imported elsewhere
# Wrap in try/except to allow importing the module even if validation fails
try:
    settings = Settings()
except Exception:
    # During testing, we might not have all required environment variables
    # This allows the module to be imported without errors
    settings = None 