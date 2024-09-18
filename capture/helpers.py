"""Some useful utility functions."""
import logging
from datetime import datetime
from http import HTTPStatus

import requests

logging.basicConfig(level=logging.INFO, format="[%(asctime)s] %(message)s")

logger = logging.getLogger()


def make_request(*, url, files) -> None:
    try:
        resp = requests.post(url, files=files)
        if resp.status_code != HTTPStatus.OK:
            logger.error("Non-ok HTTP code %d" % resp.status_code)
    except requests.exceptions.ConnectionError as e:
        logger.info("Could not connect to remote server: %s", e)


def send_image(url: str, image: bytes, filename: str) -> None:
    """
    Send_image uploads the given file to the URL via HTTP.

    Args:
        url: URL to use for upload.
        image: Raw bytes of the image
        filename: Filename of the image

    Returns:
        None

    """
    files = {filename: image}
    logger.info("Posting %s to %s", filename, url)
    make_request(url=url, files=files)


def read_and_send_image(image_queue) -> None:
    while True:
        url, image, filename = image_queue.get()
        send_image(url, image, filename)


def get_time() -> str:
    """Get_Time gets the current time and returns it as a formatted string."""
    fmt = "%Y-%m-%d_%H:%M:%S.%f"
    nowtime = datetime.now()
    return nowtime.strftime(fmt)[:-3]
