"""Capture images from a camera and detect motion using OpenCV."""
import logging
from typing import Iterable, Any, Optional
from dataclasses import dataclass

import cv2

logging.basicConfig(level=logging.INFO, format='[%(asctime)s] %(message)s')
logger = logging.getLogger()


@dataclass
class Image:
    frame: Any

    def show(self, title: str):
        cv2.imshow(title, self.frame)
        cv2.waitKey(10)

    def encode(self) -> Optional[str]:
        retval, buf = cv2.imencode(".jpg", self.frame)
        if not retval:
            return None
        return buf.tostring()

    def write(self, filename: str):
        cv2.imencode(filename, self.frame)


class MotionDetector:
    """MotionDetector captures images from a camera and detects if motion."""

    def __init__(
        self, *, cam_num=0, thresh=20, width=1280, height=960
    ) -> None:
        """
        __init__ opens the camera and initializes the background subtractor.

        Args:
            cam_num: The device ID of the camera.
            thresh: The threshold for motion detection.
            width: Image width.
            height: Image height.

        Returns:
            None

        """
        self.cam_number = cam_num
        self.threshold = thresh
        self.width = width
        self.height = height

        self._open_camera()

    def __repr__(self) -> str:
        return (
            f'MotionDetector <width={self.width}> <height={self.height}> ' +
            f'<threshold={self.threshold}> <cam_number={self.cam_number}>'
        )

    def _open_camera(self) -> None:
        self._camera = cv2.VideoCapture(self.cam_number)
        # Manually setting width and height is required for this
        # to work on OS X for some reason.
        self._camera.set(3, self.width)
        self._camera.set(4, self.height)

    def run(self) -> Iterable[Image]:
        """
        Run performs the motion detection in an infinite loop.
        """
        logger.info(
            "Running motion detection with threshold %f", self.threshold
        )
        bg = cv2.createBackgroundSubtractorMOG2()
        while True:
            return_val, frame = self._camera.read()
            if not return_val:
                logger.debug("No image from camera. Retrying...")
                continue

            foreground = bg.apply(frame)
            motion_val = cv2.mean(foreground)[0]
            if motion_val < self.threshold:
                logger.debug("Motion not detected")
                continue

            logger.info(
                "Detected motion with value %f",
                motion_val
            )
            yield Image(frame=frame)
