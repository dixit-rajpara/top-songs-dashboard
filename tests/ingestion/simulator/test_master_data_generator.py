import pytest
from faker import Faker
from top_songs.ingestion.simulator.master_data_generator import (
    generate_song_master_data,
    generate_user_master_data,
    generate_location_master_data,
)

def test_generate_song_master_data_expected():
    faker = Faker()
    songs = generate_song_master_data(10, faker)
    assert len(songs) == 10
    assert all(song.song_id for song in songs)

def test_generate_user_master_data_zero():
    faker = Faker()
    users = generate_user_master_data(0, faker)
    assert users == []

def test_generate_location_master_data_negative():
    faker = Faker()
    with pytest.raises(ValueError):
        generate_location_master_data(-5, faker) 