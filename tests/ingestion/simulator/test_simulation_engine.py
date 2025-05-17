from datetime import datetime
from top_songs.ingestion.simulator.simulation_engine import generate_historical_events, generate_live_events
from top_songs.ingestion.simulator.event_factory import EventFactory
from top_songs.core.models import PlayEventData
import pandas as pd
import os

def create_temp_master_data(tmpdir, num=3):
    # Create minimal master data files for testing
    songs = pd.DataFrame({
        "song_id": [f"song{i}" for i in range(num)],
        "title": [f"title{i}" for i in range(num)],
        "artist_name": [f"artist{i}" for i in range(num)],
        "album_name": [f"album{i}" for i in range(num)],
        "genre": ["pop"]*num,
        "duration_ms": [200000]*num,
        "release_date": ["2020-01-01"]*num,
    })
    users = pd.DataFrame({
        "user_id": [f"user{i}" for i in range(num)],
        "username": [f"user{i}" for i in range(num)],
        "email": [f"user{i}@x.com" for i in range(num)],
        "registration_date": ["2020-01-01"]*num,
        "country": ["US"]*num,
    })
    locations = pd.DataFrame({
        "location_id": [f"loc{i}" for i in range(num)],
        "city": [f"city{i}" for i in range(num)],
        "country_code": ["US"]*num,
        "latitude": [0.0]*num,
        "longitude": [0.0]*num,
    })
    for name, df in zip(["songs", "users", "locations"], [songs, users, locations]):
        path = os.path.join(tmpdir, f"{name}.csv")
        df.to_csv(path, index=False)

def test_generate_historical_events_expected(tmp_path):
    create_temp_master_data(tmp_path, num=3)
    factory = EventFactory(str(tmp_path), format="csv")
    start = datetime(2023, 1, 1, 0, 0, 0)
    end = datetime(2023, 1, 1, 1, 0, 0)
    events = generate_historical_events(factory, start, end, 5)
    assert len(events) == 5
    assert all(isinstance(e, PlayEventData) for e in events)

def test_generate_historical_events_zero(tmp_path):
    create_temp_master_data(tmp_path, num=3)
    factory = EventFactory(str(tmp_path), format="csv")
    start = datetime(2023, 1, 1, 0, 0, 0)
    end = datetime(2023, 1, 1, 1, 0, 0)
    events = generate_historical_events(factory, start, end, 0)
    assert events == []

def test_generate_historical_events_fail(tmp_path):
    create_temp_master_data(tmp_path, num=3)
    factory = EventFactory(str(tmp_path), format="csv")
    start = datetime(2023, 1, 1, 0, 0, 0)
    end = datetime(2023, 1, 1, 0, 0, 0)
    events = generate_historical_events(factory, start, end, 3)
    assert all(e.played_at == start for e in events)

def test_generate_live_events_expected(tmp_path):
    create_temp_master_data(tmp_path, num=3)
    factory = EventFactory(str(tmp_path), format="csv")
    gen = generate_live_events(factory, volume_per_minute=2, duration_seconds=1)
    events = list(gen)
    assert all(isinstance(e, PlayEventData) for e in events)

def test_generate_live_events_zero_duration(tmp_path):
    create_temp_master_data(tmp_path, num=3)
    factory = EventFactory(str(tmp_path), format="csv")
    gen = generate_live_events(factory, volume_per_minute=2, duration_seconds=0)
    # Should be an infinite generator, so just take a few
    from itertools import islice
    events = list(islice(gen, 3))
    assert len(events) == 3 