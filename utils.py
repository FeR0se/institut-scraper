import logging
from time import sleep

import requests
from requests import Response
from requests.exceptions import RequestException

logger = logging.getLogger()

def get_url(url: str, retries: int = 3, timeout: int = 10) -> Response | None:
    """Fetch a URL with retries and timeout."""
    for attempt in range(1, retries + 1):
        try:
            response = requests.get(url, timeout=timeout)
            response.raise_for_status()
            return response  # or response.json(), etc.
        except RequestException as e:
            if attempt < retries:
                sleep(1)  # backoff
            else:
                logger.error(f"Request failed after {retries} retries.")
                logger.error(f"Error: {e}")
                return None
