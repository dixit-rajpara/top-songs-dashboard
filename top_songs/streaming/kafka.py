"""
Kafka interface for the Top Songs application.
"""
from typing import Any, Dict, List, Optional, Callable, Union
import json
from pydantic import ValidationError
from confluent_kafka import Producer, Consumer, KafkaException
from confluent_kafka.admin import AdminClient, NewTopic
from top_songs.core.config import settings


class KafkaInterface:
    """Interface for Apache Kafka operations.
    
    This class provides a high-level interface for interacting with Apache Kafka
    using confluent-kafka. It handles producer and consumer operations, as well as
    administrative tasks such as topic creation.
    """
    
    def __init__(self, bootstrap_servers: Optional[str] = None,
                 topic_name: Optional[str] = None):
        """
        Initialize the Kafka interface with connection parameters.
        
        Args:
            bootstrap_servers: Comma-separated list of Kafka bootstrap servers.
                If None, uses settings.
            topic_name: Default topic name for operations. If None, uses settings.
        """
        self.bootstrap_servers = bootstrap_servers or settings.kafka.bootstrap_servers
        self.topic_name = topic_name or settings.kafka.topic_name
        
        self._producer = None
        self._consumer = None
        self._admin_client = None
    
    @property
    def producer(self) -> Producer:
        """Get the Kafka producer, creating it if necessary."""
        if self._producer is None:
            conf = {
                'bootstrap.servers': self.bootstrap_servers,
                'client.id': 'top-songs-producer'
            }
            self._producer = Producer(conf)
        return self._producer
    
    @property
    def admin_client(self) -> AdminClient:
        """Get the Kafka admin client, creating it if necessary."""
        if self._admin_client is None:
            conf = {'bootstrap.servers': self.bootstrap_servers}
            self._admin_client = AdminClient(conf)
        return self._admin_client
    
    def create_consumer(self, group_id: str, auto_offset_reset: str = 'earliest',
                        enable_auto_commit: bool = True) -> Consumer:
        """
        Create a new Kafka consumer.
        
        Args:
            group_id: Consumer group ID
            auto_offset_reset: Where to start consuming from ('earliest', 'latest')
            enable_auto_commit: Whether to auto-commit offsets
            
        Returns:
            A configured Kafka consumer
        """
        conf = {
            'bootstrap.servers': self.bootstrap_servers,
            'group.id': group_id,
            'auto.offset.reset': auto_offset_reset,
            'enable.auto.commit': enable_auto_commit
        }
        return Consumer(conf)
    
    def close(self) -> None:
        """Close all Kafka connections."""
        if self._producer is not None:
            self._producer.flush()
            # Producer has no close method, only flush
            self._producer = None
        
        if self._consumer is not None:
            self._consumer.close()
            self._consumer = None
    
    def produce(self, message: Union[str, bytes, Dict[str, Any]], 
                topic: Optional[str] = None, key: Optional[str] = None,
                headers: Optional[Dict[str, str]] = None,
                callback: Optional[Callable] = None) -> None:
        """
        Produce a message to Kafka.
        
        Args:
            message: Message to send (string, bytes, or dict to be serialized as JSON)
            topic: Topic to send to. If None, uses default topic.
            key: Optional message key
            headers: Optional message headers
            callback: Optional delivery report callback
        """
        target_topic = topic or self.topic_name
        
        # Serialize dict to JSON if needed
        if isinstance(message, dict):
            message = json.dumps(message).encode('utf-8')
        elif isinstance(message, str):
            message = message.encode('utf-8')
        
        # Convert header values to bytes if needed
        kafka_headers = None
        if headers:
            kafka_headers = [(k, v.encode('utf-8') if isinstance(v, str) else v) 
                            for k, v in headers.items()]
        
        # Produce with key if provided
        if key:
            self.producer.produce(
                topic=target_topic,
                key=key.encode('utf-8') if isinstance(key, str) else key,
                value=message,
                headers=kafka_headers,
                callback=callback
            )
        else:
            self.producer.produce(
                topic=target_topic,
                value=message,
                headers=kafka_headers,
                callback=callback
            )
        
        # Poll to trigger delivery callbacks
        self.producer.poll(0)
    
    def flush(self, timeout: Optional[float] = None) -> int:
        """
        Flush the producer to ensure all messages are delivered.
        
        Args:
            timeout: Maximum time to block (None = indefinite)
            
        Returns:
            Number of messages still in the queue
        """
        return self.producer.flush(timeout)
    
    def create_topic(self, topic_name: Optional[str] = None, 
                    num_partitions: int = 1,
                    replication_factor: int = 1) -> bool:
        """
        Create a new Kafka topic.
        
        Args:
            topic_name: Name of the topic to create. If None, uses default topic.
            num_partitions: Number of partitions for the topic
            replication_factor: Replication factor for the topic
            
        Returns:
            True if topic was created successfully, False otherwise
        """
        target_topic = topic_name or self.topic_name
        topic = NewTopic(
            target_topic,
            num_partitions=num_partitions,
            replication_factor=replication_factor
        )
        
        try:
            futures = self.admin_client.create_topics([topic])
            for topic, future in futures.items():
                future.result()  # Wait for completion
            return True
        except KafkaException:
            return False
    
    def topic_exists(self, topic_name: Optional[str] = None) -> bool:
        """
        Check if a topic exists.
        
        Args:
            topic_name: Name of the topic to check. If None, uses default topic.
            
        Returns:
            True if the topic exists, False otherwise
        """
        target_topic = topic_name or self.topic_name
        
        try:
            metadata = self.admin_client.list_topics(timeout=5)
            return target_topic in metadata.topics
        except KafkaException:
            return False
    
    def delete_topic(self, topic_name: Optional[str] = None) -> bool:
        """
        Delete a Kafka topic.
        
        Args:
            topic_name: Name of the topic to delete. If None, uses default topic.
            
        Returns:
            True if topic was deleted successfully, False otherwise
        """
        target_topic = topic_name or self.topic_name
        
        try:
            futures = self.admin_client.delete_topics([target_topic])
            for topic, future in futures.items():
                future.result()  # Wait for completion
            return True
        except KafkaException:
            return False
    
    def list_topics(self) -> List[str]:
        """
        List all topics in the Kafka cluster.
        
        Returns:
            List of topic names
        """
        try:
            metadata = self.admin_client.list_topics(timeout=5)
            return list(metadata.topics.keys())
        except KafkaException:
            return []
    
    # Higher-level methods specific to the Top Songs application
    
    def send_song_play(self, song_id: str, title: str, artist: str, 
                      user_id: str, region: str, timestamp: str) -> None:
        """
        Send a song play event to the default topic.
        
        Args:
            song_id: Unique identifier for the song
            title: Song title
            artist: Artist name
            user_id: Unique identifier for the user
            region: Geographic region code
            timestamp: ISO timestamp of the play event
        """
        message = {
            "event_type": "song_play",
            "song_id": song_id,
            "title": title,
            "artist": artist,
            "user_id": user_id,
            "region": region,
            "timestamp": timestamp
        }
        
        self.produce(message=message, key=song_id)


# Create a singleton instance for convenient import
kafka_client = None
try:
    kafka_client = KafkaInterface()
except (ImportError, ValidationError):
    # Will be initialized later when settings are available
    pass 