import csv
import json
import uuid
from typing import List
from faker import Faker
from top_songs.core.models import SongMasterData, UserMasterData, LocationMasterData

def generate_song_master_data(num_songs: int, faker: Faker) -> List[SongMasterData]:
    """
    Generate a list of SongMasterData records with unique IDs.

    Args:
        num_songs (int): Number of song records to generate.
        faker (Faker): Faker instance for generating fake data.

    Returns:
        List[SongMasterData]: List of generated song records.
    """
    if num_songs < 0:
        raise ValueError("num_songs must be non-negative")
    songs = []
    for _ in range(num_songs):
        song = SongMasterData(
            song_id=str(uuid.uuid4()),
            title=faker.sentence(nb_words=3),
            artist_name=faker.name(),
            album_name=faker.sentence(nb_words=2),
            genre=faker.word(ext_word_list=["pop", "rock", "jazz", "hiphop", "classical", "country", "electronic", "metal"]),
            duration_ms=faker.random_int(min=90000, max=420000),
            release_date=faker.date_this_century()
        )
        songs.append(song)
    return songs

def generate_user_master_data(num_users: int, faker: Faker) -> List[UserMasterData]:
    """
    Generate a list of UserMasterData records with unique IDs.

    Args:
        num_users (int): Number of user records to generate.
        faker (Faker): Faker instance for generating fake data.

    Returns:
        List[UserMasterData]: List of generated user records.
    """
    if num_users < 0:
        raise ValueError("num_users must be non-negative")
    users = []
    for _ in range(num_users):
        user = UserMasterData(
            user_id=str(uuid.uuid4()),
            username=faker.user_name(),
            email=faker.email(),
            registration_date=faker.date_this_decade(),
            country=faker.country()
        )
        users.append(user)
    return users

def generate_location_master_data(num_locations: int, faker: Faker) -> List[LocationMasterData]:
    """
    Generate a list of LocationMasterData records with unique IDs.

    Args:
        num_locations (int): Number of location records to generate.
        faker (Faker): Faker instance for generating fake data.

    Returns:
        List[LocationMasterData]: List of generated location records.
    """
    if num_locations < 0:
        raise ValueError("num_locations must be non-negative")
    locations = []
    for _ in range(num_locations):
        city = faker.city()
        country_code = faker.country_code()
        location = LocationMasterData(
            location_id=str(uuid.uuid4()),
            city=city,
            country_code=country_code,
            latitude=float(faker.latitude()),
            longitude=float(faker.longitude())
        )
        locations.append(location)
    return locations

def write_master_data_csv(records: List, output_path: str):
    """
    Write a list of Pydantic model records to a CSV file.

    Args:
        records (List): List of Pydantic model instances.
        output_path (str): Path to the output CSV file.
    """
    if not records:
        return
    with open(output_path, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=records[0].model_fields.keys())
        writer.writeheader()
        for record in records:
            writer.writerow(record.model_dump())

def write_master_data_json(records: List, output_path: str):
    """
    Write a list of Pydantic model records to a JSON file.

    Args:
        records (List): List of Pydantic model instances.
        output_path (str): Path to the output JSON file.
    """
    with open(output_path, mode="w", encoding="utf-8") as f:
        json.dump([record.model_dump() for record in records], f, indent=2, default=str) 