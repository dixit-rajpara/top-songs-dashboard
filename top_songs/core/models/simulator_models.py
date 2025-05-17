from datetime import date, datetime
from pydantic import BaseModel


class SongMasterData(BaseModel):
    """
    Represents a song in the master data set.

    Attributes:
        song_id (str): Unique identifier for the song (UUID).
        title (str): Title of the song.
        artist_name (str): Name of the artist.
        album_name (str): Name of the album.
        genre (str): Genre of the song.
        duration_ms (int): Duration of the song in milliseconds.
        release_date (date): Release date of the song.
    """
    song_id: str
    title: str
    artist_name: str
    album_name: str
    genre: str
    duration_ms: int
    release_date: date


class UserMasterData(BaseModel):
    """
    Represents a user in the master data set.

    Attributes:
        user_id (str): Unique identifier for the user (UUID).
        username (str): Username of the user.
        email (str): Email address of the user.
        registration_date (date): Date the user registered.
        country (str): Country of the user.
    """
    user_id: str
    username: str
    email: str
    registration_date: date
    country: str


class LocationMasterData(BaseModel):
    """
    Represents a location or region in the master data set.

    Attributes:
        location_id (str): Unique identifier for the location (UUID or composite key).
        city (str): City name.
        country_code (str): Country code (e.g., 'US', 'GB').
        latitude (float): Latitude coordinate.
        longitude (float): Longitude coordinate.
    """
    location_id: str
    city: str
    country_code: str
    latitude: float
    longitude: float


class PlayEventData(BaseModel):
    """
    Represents a transactional play event.

    Attributes:
        event_id (str): Unique identifier for the event (UUID).
        song_id (str): Song ID (FK to SongMasterData.song_id).
        user_id (str): User ID (FK to UserMasterData.user_id).
        location_id (str): Location ID (FK to LocationMasterData.location_id).
        played_at (datetime): Timestamp of when the song was played.
        play_duration_ms (int): Actual duration the user listened (<= SongMasterData.duration_ms).
        device_type (str): Device type (e.g., 'mobile', 'desktop', 'tablet').
    """
    event_id: str
    song_id: str
    user_id: str
    location_id: str
    played_at: datetime
    play_duration_ms: int
    device_type: str 