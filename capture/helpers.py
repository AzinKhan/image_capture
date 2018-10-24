import logging
from datetime import datetime

import requests

logging.basicConfig(level=logging.INFO,
                    format='[%(asctime)s] %(message)s')

logger = logging.getLogger()


def send_image(info_queue):
    while True:
        url, image_bytes, filename = info_queue.get()
        files = {filename: image_bytes}
        try:
            logger.info('Posting %s to %s', filename, url)
            resp = requests.post(url, files=files)
            if resp.status_code != 200:
                logger.error("Non-ok HTTP code %d" % resp.status_code)
        except requests.exceptions.ConnectionError as e:
            logger.info("Could not connect to remote server: %s", e)


def getTime():
    fmt = '%Y-%m-%d_%H:%M:%S.%f'
    nowtime = datetime.now()
    return nowtime.strftime(fmt)[:-3]