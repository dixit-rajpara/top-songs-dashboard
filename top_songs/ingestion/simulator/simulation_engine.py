from datetime import datetime, timedelta, UTC
from typing import List, Generator
from top_songs.ingestion.simulator.event_factory import EventFactory
from top_songs.core.models import PlayEventData
import time

def generate_historical_events(
    event_factory: EventFactory,
    start_datetime: datetime,
    end_datetime: datetime,
    volume: int,
) -> List[PlayEventData]:
    """
    Generate a list of PlayEventData for the specified historical period and volume.

    Args:
        event_factory (EventFactory): The event factory to create events.
        start_datetime (datetime): Start of the historical period.
        end_datetime (datetime): End of the historical period.
        volume (int): Total number of events to generate.

    Returns:
        List[PlayEventData]: List of generated play events.
    """
    total_seconds = (end_datetime - start_datetime).total_seconds()
    events = []
    for i in range(volume):
        # Distribute timestamps evenly/randomly within the range
        offset = total_seconds * (i / volume)
        played_at = start_datetime + timedelta(seconds=offset)
        event = event_factory.create_event(played_at=played_at)
        events.append(event)
    return events

def generate_live_events(
    event_factory: EventFactory,
    volume_per_minute: int = 60,
    duration_seconds: int = 0,
) -> Generator[PlayEventData, None, None]:
    """
    Generate PlayEventData in live mode at a target rate for a given duration.

    Args:
        event_factory (EventFactory): The event factory to create events.
        volume_per_minute (int): Target number of events per minute.
        duration_seconds (int): Duration to run the simulation (0 = indefinite).

    Yields:
        PlayEventData: The next generated play event.
    """
    interval = 60.0 / volume_per_minute if volume_per_minute > 0 else 1.0
    start_time = time.time()
    count = 0
    while True:
        now = time.time()
        if duration_seconds > 0 and (now - start_time) >= duration_seconds:
            break
        event = event_factory.create_event(played_at=datetime.now(UTC))
        yield event
        count += 1
        time.sleep(interval) 