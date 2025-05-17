import pytest
import os
import pandas as pd
from top_songs.ingestion.simulator.event_factory import EventFactory
from top_songs.core.models import PlayEventData

def create_temp_master_data(tmpdir, format="csv", num=3):
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
        path = os.path.join(tmpdir, f"{name}.{format}")
        if format == "csv":
            df.to_csv(path, index=False)
        else:
            df.to_json(path, orient="records")

def test_event_factory_create_event(tmp_path):
    create_temp_master_data(tmp_path, format="csv", num=3)
    factory = EventFactory(str(tmp_path), format="csv")
    event = factory.create_event()
    assert isinstance(event, PlayEventData)
    assert event.song_id.startswith("song")
    assert event.user_id.startswith("user")
    assert event.location_id.startswith("loc")

def test_event_factory_empty_master_data(tmp_path):
    # Create empty master data files
    for name in ["songs", "users", "locations"]:
        pd.DataFrame().to_csv(tmp_path / f"{name}.csv", index=False)
    with pytest.raises(ValueError):
        EventFactory(str(tmp_path), format="csv").create_event()

def test_event_factory_invalid_format(tmp_path):
    create_temp_master_data(tmp_path, format="csv", num=1)
    with pytest.raises(ValueError):
        EventFactory(str(tmp_path), format="xml") 