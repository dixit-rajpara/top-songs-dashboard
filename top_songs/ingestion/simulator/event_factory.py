import os
import random
import uuid
from datetime import datetime, UTC
from typing import Optional
import pandas as pd
from faker import Faker
from top_songs.core.models import SongMasterData, UserMasterData, LocationMasterData, PlayEventData

def _load_csv_or_json(path: str, model_cls):
    """
    Load master data from CSV or JSON file and return a list of Pydantic model instances.
    """
    try:
        if path.endswith(".csv"):
            df = pd.read_csv(path)
            return [model_cls(**row) for row in df.to_dict(orient="records")]
        elif path.endswith(".json"):
            df = pd.read_json(path)
            return [model_cls(**row) for row in df.to_dict(orient="records")]
        else:
            raise ValueError(f"Unsupported file format: {path}")
    except pd.errors.EmptyDataError:
        return []

class EventFactory:
    """
    Factory for creating PlayEventData instances using loaded master data.
    """
    def __init__(self, master_data_dir: str, format: str = "csv"):
        """
        Initialize the EventFactory and load master data.

        Args:
            master_data_dir (str): Directory containing master data files.
            format (str): File format ('csv' or 'json').
        """
        self.faker = Faker()
        self.songs = _load_csv_or_json(os.path.join(master_data_dir, f"songs.{format}"), SongMasterData)
        self.users = _load_csv_or_json(os.path.join(master_data_dir, f"users.{format}"), UserMasterData)
        self.locations = _load_csv_or_json(os.path.join(master_data_dir, f"locations.{format}"), LocationMasterData)

    def create_event(self, played_at: Optional[datetime] = None) -> PlayEventData:
        """
        Create a PlayEventData instance with random but valid references to master data.

        Args:
            played_at (Optional[datetime]): Timestamp for the play event. If None, uses now.

        Returns:
            PlayEventData: The generated play event.
        """
        if not self.songs or not self.users or not self.locations:
            raise ValueError("Master data is empty. Please provide non-empty songs, users, and locations data.")
        song = random.choice(self.songs)
        user = random.choice(self.users)
        location = random.choice(self.locations)
        play_duration_ms = random.randint(10000, song.duration_ms)
        device_type = self.faker.random_element(["mobile", "desktop", "tablet"])
        return PlayEventData(
            event_id=str(uuid.uuid4()),
            song_id=song.song_id,
            user_id=user.user_id,
            location_id=location.location_id,
            played_at=played_at or datetime.now(UTC),
            play_duration_ms=play_duration_ms,
            device_type=device_type,
        ) 