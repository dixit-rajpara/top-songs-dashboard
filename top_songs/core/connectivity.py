"""
Service connectivity checks for Top Songs Dashboard.
"""
from top_songs.core.config import settings
from top_songs.storage.database.postgres import PostgresInterface
from top_songs.storage.object_store.s3 import ObjectStoreInterface
from top_songs.streaming.kafka import KafkaInterface

async def check_postgres_connection() -> bool:
    """
    Check if PostgreSQL connection is working.

    Returns:
        bool: True if connection is successful, False otherwise.
    """
    if settings.postgres is None:
        return False
    pg = PostgresInterface()
    try:
        await pg.connect()
        await pg.disconnect()
        return True
    except Exception:
        return False

def check_kafka_connection() -> bool:
    """
    Check if Kafka connection is working.

    Returns:
        bool: True if connection is successful, False otherwise.
    """
    try:
        kafka = KafkaInterface()
        # Simply checking if we can list topics is sufficient
        # to verify connection to Kafka brokers
        kafka.list_topics()
        return True
    except Exception:
        return False

def check_object_store_connection() -> bool:
    """
    Check if Object Store (MinIO/S3) connection is working.

    Returns:
        bool: True if connection is successful, False otherwise.
    """
    if settings.object_store is None:
        return False
    try:
        obj_store = ObjectStoreInterface()
        obj_store.client.list_buckets()
        return True
    except Exception:
        return False 