#!/usr/bin/env python3

import cv2
import requests
import logging

logging.basicConfig(level=logging.INFO,
                    format='[%(asctime)s] %(message)s')

logger = logging.getLogger()

def send_image(url, image_bytes):
    files = {"image": image_bytes}
    r = requests.post(url, files=files)
    return r

class ImageInfo(object):
    def __init__(self):
        self.motion_val = 0.0

class MotionDetector(object):
     
    def __init__(self, cam_num=0, thresh=20, width=1280, height=960):
        self.cam_number = cam_num
        self.threshold = thresh
        self.width = width
        self.height = height
        self.__current_frame = ImageInfo()
        self.__open_camera__()
        self.__bg = cv2.createBackgroundSubtractorMOG2()

    def __open_camera__(self):
        self.__camera = cv2.VideoCapture(self.cam_number)
        # Manually setting width and height is required for this 
        # to work on OS X for some reason.
        self.__camera.set(3, self.width)
        self.__camera.set(4, self.height)

    def __average_motion__(self, frame, channel):
        return cv2.mean(frame)[channel]
    
    def __read__camera__(self):
        return_val, frame = self.__camera.read()
        if return_val:
            self.__current_frame.frame = frame
        return return_val

    def __detect_motion__(self):
        foreground = self.__bg.apply(self.__current_frame.frame)
        self.__current_frame.motion_val = self.__average_motion__(foreground, 0)
    
    def run(self):
        logger.info("Running motion detection with threshold %f", self.threshold)
        while True:
            try:
                if self.__read__camera__():
                    logger.debug("Checking motion value...")
                    self.__detect_motion__()
                    if self.__current_frame.motion_val >= self.threshold:
                        logger.info("Detected motion with value %f" % self.__current_frame.motion_val)
                        yield self.__current_frame
                    else:
                        logger.debug("Motion not detected")
                else:
                    logger.debug("No image from camera. Retrying...")
            except KeyboardInterrupt:
                logger.info("Motion detection stopped by KeyboardInterrupt")
                raise StopIteration


if __name__ == "__main__":
    detector = MotionDetector(cam_num=0, thresh=10)
    for img in detector.run():
        #cv2.imshow("Motion", img.frame)
        #cv2.waitKey(10)
        pass
