"""Capture images from a camera and detect motion using OpenCV."""
import logging

from cv2 import (
    createBackgroundSubtractorMOG2, VideoCapture, mean,
)

logging.basicConfig(level=logging.INFO, format='[%(asctime)s] %(message)s')

logger = logging.getLogger()


class ImageInfo:
    """A simple record class."""

    motion_val = 0.0
    frame = None


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

        self._current_frame = ImageInfo()
        self._open_camera()
        self._bg = createBackgroundSubtractorMOG2()

    def __repr__(self) -> str:
        return (
            f'MotionDetector <width={self.width}> <height={self.height}> ' +
            f'<threshold={self.threshold}> <cam_number={self.cam_number}>'
        )

    def _open_camera(self) -> None:
        self._camera = VideoCapture(self.cam_number)
        # Manually setting width and height is required for this
        # to work on OS X for some reason.
        self._camera.set(3, self.width)
        self._camera.set(4, self.height)

    @staticmethod
    def _average_motion(frame, channel) -> float:
        return mean(frame)[channel]

    def _read_camera(self) -> bool:
        return_val, frame = self._camera.read()
        if return_val:
            self._current_frame.frame = frame
        return return_val

    def _detect_motion(self) -> None:
        foreground = self._bg.apply(self._current_frame.frame)
        self._current_frame.motion_val = self._average_motion(foreground, 0)

    def run(self, queue) -> None:
        """
        Run performs the motion detection in an infinite loop.

        Args:
            queue: A queue in which to put the results.

        Returns:
            None

        """
        logger.info(
            "Running motion detection with threshold %f", self.threshold
        )
        while True:
            if self._read_camera():
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
