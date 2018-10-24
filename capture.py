import requests
import logging
import argparse
import datetime
from multiprocessing import Process, Queue

from cv2 import (
    createBackgroundSubtractorMOG2, VideoCapture, mean,
    imencode, waitKey, imwrite, imshow
)

logging.basicConfig(level=logging.INFO,
                    format='[%(asctime)s] %(message)s')

logger = logging.getLogger()


class ImageInfo:
    motion_val = 0.0
    frame = None


class MotionDetector:

    def __init__(self, *, cam_num=0, thresh=20, width=1280, height=960):
        self.cam_number = cam_num
        self.threshold = thresh
        self.width = width
        self.height = height

        self._current_frame = ImageInfo()
        self._open_camera()
        self._bg = createBackgroundSubtractorMOG2()

    def _open_camera(self):
        self._camera = VideoCapture(self.cam_number)
        # Manually setting width and height is required for this
        # to work on OS X for some reason.
        self._camera.set(3, self.width)
        self._camera.set(4, self.height)

    @staticmethod
    def _average_motion(frame, channel):
        return mean(frame)[channel]

    def _read__camera(self):
        return_val, frame = self._camera.read()
        if return_val:
            self._current_frame.frame = frame
        return return_val

    def _detect_motion(self):
        foreground = self._bg.apply(self._current_frame.frame)
        self._current_frame.motion_val = self._average_motion(foreground, 0)

    def run(self, queue):
        logger.info(
            "Running motion detection with threshold %f", self.threshold
        )
        while True:
            if self._read__camera():
                logger.debug("Checking motion value...")
                self._detect_motion()
                if self._current_frame.motion_val >= self.threshold:
                    logger.info(
                        "Detected motion with value %f",
                        self._current_frame.motion_val
                    )
                    queue.put(self._current_frame)
                else:
                    logger.debug("Motion not detected")
            else:
                logger.debug("No image from camera. Retrying...")


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
    nowtime = datetime.datetime.now()
    return nowtime.strftime(fmt)[:-3]


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="A simple motion detector")
    parser.add_argument(
        "--threshold", metavar="threshold", type=float, default=10, nargs='?',
        help="Threshold for motion detection."
    )
    parser.add_argument(
        "--width", metavar="width", type=int, default=1280,
        nargs='?', help="Width of image"
    )
    parser.add_argument(
        "--height", metavar="height", type=int, default=960,
        nargs='?', help="Height of image"
    )
    parser.add_argument(
        "--cam", metavar="cam", type=int, default=0,
        nargs='?', help="Camera ID"
    )
    parser.add_argument("--show", action="store_true", help="Show images")
    parser.add_argument(
        "--write", action="store_true", help="Write images to file"
    )
    parser.add_argument(
        "--send", action="store_true", help="Upload images to remote server"
    )
    parser.add_argument(
        "--url", metavar="url", type=str, default="http://0.0.0.0:8000/",
        nargs='?', help="Remote URL"
    )
    parser.add_argument(
        "--verbose", "-v", action="store_true", help="Allow debug logs."
    )
    args = parser.parse_args()
    if args.verbose:
        logger.setLevel(logging.DEBUG)
    detector = MotionDetector(
        cam_num=args.cam, thresh=args.threshold,
        width=args.width, height=args.height
    )
    image_queue = Queue()
    info_queue = Queue()

    sender = Process(target=send_image, args=(info_queue,))
    sender.daemon = True
    sender.start()

    det = Process(target=detector.run, args=(image_queue,))
    det.daemon = True
    det.start()

    running = True
    while running:
        try:
            img = image_queue.get()
            filename = getTime() + ".jpg"
            if args.show:
                imshow("Motion", img.frame)
                waitKey(10)

            if args.send:
                retval, buf = imencode(".jpg", img.frame)
                if retval:
                    info_queue.put((args.url, buf.tostring(), filename))
                else:
                    logger.error("Could not  encode image")

            if args.write:
                imwrite(filename, img.frame)
                waitKey(10)
        except KeyboardInterrupt:
            logger.info('Stopping processes...')
            sender.terminate()
            det.terminate()
            sender.join()
            det.join()
            logger.info('All processes stopped.')
            running = False
