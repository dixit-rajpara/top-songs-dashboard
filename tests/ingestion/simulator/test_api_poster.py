from unittest.mock import patch, MagicMock
from top_songs.ingestion.simulator.api_poster import APIPoster
from top_songs.core.models import PlayEventData
from datetime import datetime, UTC

def make_event():
    return PlayEventData(
        event_id="e1",
        song_id="s1",
        user_id="u1",
        location_id="l1",
        played_at=datetime.now(UTC),
        play_duration_ms=1000,
        device_type="mobile",
    )

def test_api_poster_success(monkeypatch):
    poster = APIPoster("http://fake/api")
    event = make_event()
    with patch("httpx.post") as mock_post:
        mock_post.return_value.raise_for_status = MagicMock()
        assert poster.post_event(event)

def test_api_poster_timeout(monkeypatch):
    poster = APIPoster("http://fake/api")
    event = make_event()
    with patch("httpx.post", side_effect=Exception("timeout")):
        assert not poster.post_event(event)

def test_api_poster_http_error(monkeypatch):
    poster = APIPoster("http://fake/api", max_retries=2)
    event = make_event()
    class DummyHTTPError(Exception): pass
    with patch("httpx.post", side_effect=DummyHTTPError("fail")):
        assert not poster.post_event(event) 