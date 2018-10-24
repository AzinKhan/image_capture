import logging

from cv2 import (
    createBackgroundSubtractorMOG2, VideoCapture, mean,
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
