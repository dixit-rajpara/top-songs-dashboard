import pytest
from pydantic import ValidationError
from top_songs.core.config.settings import (
    Settings, 
    KafkaSettings, 
    ObjectStoreSettings, 
    PostgresSettings, 
    ApiSettings, 
    SparkSettings,
    PrefectSettings
)


class TestKafkaSettings:
    """Tests for KafkaSettings class."""
    
    def test_default_values(self):
        """Test that default values are set correctly."""
        settings = KafkaSettings()
        assert settings.bootstrap_servers == "localhost:9092"
        assert settings.topic_name == "song-plays"
    
    def test_manual_override(self):
        """Test that values can be manually overridden."""
        settings = KafkaSettings(bootstrap_servers="kafka:9092", topic_name="custom-topic")
        assert settings.bootstrap_servers == "kafka:9092"
        assert settings.topic_name == "custom-topic"


class TestObjectStoreSettings:
    """Tests for ObjectStoreSettings class."""
    
    def test_required_values(self):
        """Test that required values raise error if not provided."""
        with pytest.raises(ValidationError):
            ObjectStoreSettings()
    
    def test_with_required_values(self):
        """Test that instance is created when required values are provided."""
        settings = ObjectStoreSettings(
            access_key="test-access-key",
            secret_key="test-secret-key"
        )
        assert settings.access_key == "test-access-key"
        assert settings.secret_key == "test-secret-key"
        assert settings.endpoint == "localhost:9000"  # Default value
    
    def test_all_values_override(self):
        """Test that all values can be overridden."""
        settings = ObjectStoreSettings(
            endpoint="minio:9000",
            access_key="custom-access-key",
            secret_key="custom-secret-key",
            secure=True,
            bucket_name="custom-bucket",
            region="eu-west-1"
        )
        assert settings.endpoint == "minio:9000"
        assert settings.access_key == "custom-access-key"
        assert settings.secret_key == "custom-secret-key"
        assert settings.secure is True
        assert settings.bucket_name == "custom-bucket"
        assert settings.region == "eu-west-1"


class TestPostgresSettings:
    """Tests for PostgresSettings class."""
    
    def test_required_values(self):
        """Test that postgres_dsn is required."""
        with pytest.raises(ValidationError):
            PostgresSettings()
    
    def test_valid_dsn(self):
        """Test that a valid PostgreSQL DSN is accepted."""
        test_dsn = "postgresql://user:pass@localhost:5432/dbname"
        settings = PostgresSettings(postgres_dsn=test_dsn)
        assert str(settings.postgres_dsn) == test_dsn
    
    def test_invalid_dsn(self):
        """Test that an invalid PostgreSQL DSN is rejected."""
        test_dsn = "invalid-dsn-format"
        with pytest.raises(ValidationError):
            PostgresSettings(postgres_dsn=test_dsn)


class TestApiSettings:
    """Tests for ApiSettings class."""
    
    def test_default_values(self):
        """Test that default values are set correctly."""
        settings = ApiSettings()
        assert settings.host == "0.0.0.0"
        assert settings.port == 8000
        assert settings.debug is False
        assert settings.workers == 4
    
    def test_manual_override(self):
        """Test that values can be manually overridden."""
        settings = ApiSettings(
            host="127.0.0.1",
            port=9000,
            debug=True,
            workers=8
        )
        assert settings.host == "127.0.0.1"
        assert settings.port == 9000
        assert settings.debug is True
        assert settings.workers == 8


class TestSparkSettings:
    """Tests for SparkSettings class."""
    
    def test_default_values(self):
        """Test that default values are set correctly."""
        settings = SparkSettings()
        assert settings.master == "local[*]"
        assert settings.app_name == "TopSongsDashboard"
        assert settings.checkpoint_location == "/tmp/checkpoint"
        assert settings.batch_interval_seconds == 60
    
    def test_manual_override(self):
        """Test that values can be manually overridden."""
        settings = SparkSettings(
            master="spark://spark-master:7077",
            app_name="CustomAppName",
            checkpoint_location="/custom/checkpoint",
            batch_interval_seconds=120
        )
        assert settings.master == "spark://spark-master:7077"
        assert settings.app_name == "CustomAppName"
        assert settings.checkpoint_location == "/custom/checkpoint"
        assert settings.batch_interval_seconds == 120


class TestPrefectSettings:
    """Tests for PrefectSettings class."""
    
    def test_default_values(self):
        """Test that default values are set correctly."""
        settings = PrefectSettings()
        assert settings.api_url == "http://localhost:4200/api"
        assert settings.ui_port == 4200
        assert settings.agent_queue_name == "default"
        assert settings.flow_storage_path == "./storage/prefect"
    
    def test_manual_override(self):
        """Test that values can be manually overridden."""
        settings = PrefectSettings(
            api_url="http://prefect-server:4200/api",
            ui_port=4201,
            agent_queue_name="custom-queue",
            flow_storage_path="/custom/storage/path"
        )
        assert settings.api_url == "http://prefect-server:4200/api"
        assert settings.ui_port == 4201
        assert settings.agent_queue_name == "custom-queue"
        assert settings.flow_storage_path == "/custom/storage/path"


class TestSettings:
    """Tests for the main Settings class."""
    
    def test_custom_settings(self):
        """Test creating Settings with custom values."""
        kafka = KafkaSettings(bootstrap_servers="kafka:9092")
        object_store = ObjectStoreSettings(access_key="test-key", secret_key="test-secret")
        postgres = PostgresSettings(postgres_dsn="postgresql://user:pass@postgres:5432/testdb")
        api = ApiSettings(port=9000)
        spark = SparkSettings(master="spark://spark-master:7077")
        prefect = PrefectSettings(ui_port=4201)
        
        settings = Settings(
            environment="test",
            debug=False,
            project_name="Test Project",
            kafka=kafka,
            object_store=object_store,
            postgres=postgres,
            api=api,
            spark=spark,
            prefect=prefect
        )
        
        # Test top-level settings
        assert settings.environment == "test"
        assert settings.debug is False
        assert settings.project_name == "Test Project"
        
        # Test nested settings
        assert settings.kafka.bootstrap_servers == "kafka:9092"
        assert settings.object_store is not None
        assert settings.object_store.access_key == "test-key"
        assert settings.object_store.secret_key == "test-secret"
        assert settings.postgres is not None
        assert str(settings.postgres.postgres_dsn) == "postgresql://user:pass@postgres:5432/testdb"
        assert settings.api.port == 9000
        assert settings.spark.master == "spark://spark-master:7077"
        assert settings.prefect.ui_port == 4201
    
    def test_optional_settings(self):
        """Test that Settings works with None values for optional nested settings."""
        settings = Settings(object_store=None, postgres=None)
        
        assert settings.object_store is None
        assert settings.postgres is None
        
        # But other settings should use defaults
        assert settings.kafka is not None
        assert settings.api is not None
        assert settings.spark is not None
        assert settings.prefect is not None 