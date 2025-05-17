import httpx
from typing import Optional
from top_songs.core.models import PlayEventData
import logging


class APIPoster:
    """
    Handles posting PlayEventData to the configured API endpoint.
    """
    def __init__(self, api_endpoint: str, max_retries: int = 3):
        """
        Initialize the APIPoster.

        Args:
            api_endpoint (str): The URL of the API endpoint to post play events.
            max_retries (int): Maximum number of retries for failed requests.
        """
        self.api_endpoint = api_endpoint
        self.max_retries = max_retries
        self.logger = logging.getLogger("APIPoster")

    def post_event(self, event: PlayEventData, timeout: Optional[float] = 5.0) -> bool:
        """
        Post a single PlayEventData instance to the API endpoint.

        Args:
            event (PlayEventData): The play event to post.
            timeout (Optional[float]): Request timeout in seconds.

        Returns:
            bool: True if the post was successful, False otherwise.
        """
        for attempt in range(1, self.max_retries + 1):
            try:
                response = httpx.post(
                    self.api_endpoint,
                    json=event.model_dump(),
                    timeout=timeout,
                )
                response.raise_for_status()
                return True
            except Exception as e:
                self.logger.error(f"Attempt {attempt}: Failed to post event {event.event_id}: {e}")
                if attempt == self.max_retries:
                    return False 