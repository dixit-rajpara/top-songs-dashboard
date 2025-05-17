"""
Simulator CLI command implementations for master data generation and simulation run logic.
"""
import os
import threading
from datetime import datetime
import logging
from top_songs.ingestion.simulator.master_data_generator import (
    generate_song_master_data,
    generate_user_master_data,
    generate_location_master_data,
    write_master_data_csv,
    write_master_data_json,
)
from top_songs.ingestion.simulator.event_factory import EventFactory
from top_songs.ingestion.simulator.api_poster import APIPoster
from top_songs.ingestion.simulator.simulation_engine import generate_historical_events, generate_live_events

def generate_master_data_command(
    output_dir: str = "data/master/",
    num_songs: int = 1000,
    num_users: int = 5000,
    num_locations: int = 100,
    format: str = "csv",
):
    """
    Generate master data for songs, users, and locations, and write to files.
    """
    from typer import echo
    from faker import Faker
    faker = Faker()
    os.makedirs(output_dir, exist_ok=True)

    echo(f"Generating {num_songs} songs, {num_users} users, {num_locations} locations...")
    songs = generate_song_master_data(num_songs, faker)
    users = generate_user_master_data(num_users, faker)
    locations = generate_location_master_data(num_locations, faker)

    if format == "csv":
        write_master_data_csv(songs, os.path.join(output_dir, "songs.csv"))
        write_master_data_csv(users, os.path.join(output_dir, "users.csv"))
        write_master_data_csv(locations, os.path.join(output_dir, "locations.csv"))
    elif format == "json":
        write_master_data_json(songs, os.path.join(output_dir, "songs.json"))
        write_master_data_json(users, os.path.join(output_dir, "users.json"))
        write_master_data_json(locations, os.path.join(output_dir, "locations.json"))
    else:
        echo(f"Unsupported format: {format}")
        return

    echo(f"Master data generated in {output_dir} (format: {format})")

def run_simulation_command(
    master_data_dir: str = "data/master/",
    api_endpoint: str = "http://localhost:8000/play",
    threads: int = 4,
    volume: int = 10000,
    historical: bool = False,
    live: bool = False,
    start_datetime: str = None,
    end_datetime: str = None,
    posting_rate: float = 10.0,
    duration_seconds: int = 0,
    format: str = "csv",
):
    """
    Run the data simulator in historical or live mode with concurrency support.
    """
    logger = logging.getLogger("Simulator")
    event_factory = EventFactory(master_data_dir, format=format)
    api_poster = APIPoster(api_endpoint)

    def post_events(events):
        for event in events:
            api_poster.post_event(event)

    if historical:
        if not start_datetime or not end_datetime:
            logger.error("--start-datetime and --end-datetime are required for historical mode.")
            return
        logger.info(f"Starting historical simulation: {volume} events from {start_datetime} to {end_datetime}...")
        start_dt = datetime.fromisoformat(start_datetime)
        end_dt = datetime.fromisoformat(end_datetime)
        events = generate_historical_events(event_factory, start_dt, end_dt, volume)
        chunk_size = (len(events) + threads - 1) // threads
        thread_list = []
        for i in range(threads):
            chunk = events[i*chunk_size:(i+1)*chunk_size]
            t = threading.Thread(target=post_events, args=(chunk,))
            t.start()
            thread_list.append(t)
        for t in thread_list:
            t.join()
        logger.info("Historical simulation complete.")
    elif live:
        logger.info(f"Starting live simulation: {volume} events/minute for {duration_seconds or 'infinite'} seconds...")
        def live_worker():
            for event in generate_live_events(event_factory, volume_per_minute=volume, duration_seconds=duration_seconds):
                api_poster.post_event(event)
        thread_list = []
        for _ in range(threads):
            t = threading.Thread(target=live_worker)
            t.start()
            thread_list.append(t)
        for t in thread_list:
            t.join()
        logger.info("Live simulation complete.")
    else:
        logger.error("Please specify either --historical or --live mode.") 