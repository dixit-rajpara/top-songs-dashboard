import logging
from fastapi import FastAPI, status, HTTPException
from top_songs.core.models.simulator_models import PlayEventData
from top_songs.streaming.kafka import KafkaInterface
from top_songs.core.config.logger import setup_logging

setup_logging()

app = FastAPI(title="Top Songs Ingestion API", version="0.1.0")
kafka = KafkaInterface()
logger = logging.getLogger("IngestionAPI")

@app.get("/health", status_code=status.HTTP_200_OK)
def health_check():
    """
    Health check endpoint for readiness/liveness probes.
    """
    return {"status": "ok"}

@app.post("/play", status_code=status.HTTP_201_CREATED)
def post_play_event(event: PlayEventData):
    """
    Receive a song play event and forward to Kafka.
    """
    try:
        kafka.produce(event.model_dump(mode='json'))
        return {"message": "Play event received", "event_id": event.event_id}
    except Exception as e:
        logger.error(f"Failed to produce event to Kafka: {e}")
        raise HTTPException(status_code=500, detail="Failed to forward event to Kafka.")

def create_app() -> FastAPI:
    """
    App factory for production use (importable by Gunicorn/Uvicorn).
    """
    return app 