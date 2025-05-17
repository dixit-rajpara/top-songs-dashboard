import pytest
from fastapi.testclient import TestClient
from top_songs.ingestion.api.app import app
from top_songs.core.models.simulator_models import PlayEventData
from datetime import datetime, UTC
from unittest.mock import patch

client = TestClient(app)

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

@patch("top_songs.ingestion.api.app.kafka.produce")
def test_post_play_event(mock_produce):
    payload = {
        "event_id": "test-event-1",
        "song_id": "song-1",
        "user_id": "user-1",
        "location_id": "loc-1",
        "played_at": datetime.now(UTC).isoformat(),
        "play_duration_ms": 123456,
        "device_type": "mobile"
    }
    response = client.post("/play", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["event_id"] == payload["event_id"]
    assert data["message"] == "Play event received"
    mock_produce.assert_called_once()

@patch("top_songs.ingestion.api.app.kafka.produce", side_effect=Exception("kafka error"))
def test_post_play_event_kafka_failure(mock_produce):
    payload = {
        "event_id": "test-event-2",
        "song_id": "song-2",
        "user_id": "user-2",
        "location_id": "loc-2",
        "played_at": datetime.now(UTC).isoformat(),
        "play_duration_ms": 654321,
        "device_type": "desktop"
    }
    response = client.post("/play", json=payload)
    assert response.status_code == 500
    assert response.json()["detail"] == "Failed to forward event to Kafka."
    mock_produce.assert_called_once() 