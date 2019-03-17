"""Some useful utility functions."""
import logging
from datetime import datetime
from http import HTTPStatus

import requests

logging.basicConfig(level=logging.INFO,
                    format='[%(asctime)s] %(message)s')

logger = logging.getLogger()


def make_request(*, url, files) -> None:
    try:
        resp = requests.post(url, files=files)
        if resp.status_code != HTTPStatus.OK:
            logger.error("Non-ok HTTP code %d" % resp.status_code)
    except requests.exceptions.ConnectionError as e:
        logger.info("Could not connect to remote server: %s", e)


def send_image(info_queue) -> None:
    """
    Send_image uploads files from a queue via HTTP requests.

    Args:
        info_queue: The queue from which to read values.

    Returns:
        None

    """
    while True:
        url, image_bytes, filename = info_queue.get()
        files = {filename: image_bytes}
        logger.info('Posting %s to %s', filename, url)
        make_request(url=url, files=files)


def getTime() -> str:
    """Get_Time gets the current time and returns it as a formatted string."""
    fmt = '%Y-%m-%d_%H:%M:%S.%f'
    nowtime = datetime.now()
    return nowtime.strftime(fmt)[:-3]
