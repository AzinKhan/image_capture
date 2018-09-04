#!/usr/bin/env python3

import cv2
import requests
import logging
import argparse
import os
import datetime

logging.basicConfig(level=logging.INFO,
                    format='[%(asctime)s] %(message)s')

logger = logging.getLogger()


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

def send_image(url, image_bytes, filename):
    files = {filename: image_bytes}
    r = requests.post(url, files=files)
    return r

def getTime():
<<<<<<< HEAD
    fmt = ("%Y-%m-%d_%H:%M:%S.%f")[:-3]
=======
    fmt = "%Y-%m-%d_%H-%M-%S"
>>>>>>> 9e6cbd69f5d46c0db07bee9bbdbaf210cc593855
    nowtime = datetime.datetime.now()
    return nowtime.strftime(fmt)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="A simple motion detector")
    parser.add_argument("--threshold", metavar="threshold", type=float, default=10, nargs='?', help="Threshold for motion detection.")
    parser.add_argument("--width", metavar="width", type=int, default=1280, nargs='?', help="Width of image")
    parser.add_argument("--height", metavar="height", type=int, default=960, nargs='?', help="Height of image")
    parser.add_argument("--cam", metavar="cam", type=int, default=0, nargs='?', help="Camera ID")
    parser.add_argument("--show", metavar="show", type=bool, default=False, nargs='?', help="Show images")
    parser.add_argument("--write", metavar="write", type=bool, default=False, nargs='?', help="Write images to file" )
    parser.add_argument("--send", metavar="send", type=bool, default=False, nargs='?', help="Upload images to remote server" )
    parser.add_argument("--url", metavar="url", type=str, default="http://0.0.0.0:8000/", nargs='?', help="Remote URL")
    args = parser.parse_args()
    detector = MotionDetector(cam_num=args.cam, thresh=args.threshold, width=args.width, height=args.height)
    for img in detector.run():
        filename = getTime() + ".jpg"
<<<<<<< HEAD
=======
        print(filename)
>>>>>>> 9e6cbd69f5d46c0db07bee9bbdbaf210cc593855
        if args.show:
            cv2.imshow("Motion", img.frame)
            cv2.waitKey(10)

        
        if args.send:
            retval, buf = cv2.imencode(".jpg", img.frame)
            if retval:
                try:
                    resp = send_image(args.url, buf.tostring(), filename)
                    if resp.status_code != 200:
                        logger.error("Non-ok HTTP code %d" % resp.status_code)
                except requests.exceptions.ConnectionError as e:
                    print(e)
                    logger.info("Could not connect to remote server")
<<<<<<< HEAD
            else:
                logger.error("Could not  encode image")
=======
                    #logger.info("Writing image to file until connection is made")
        else:
            logger.error("Could not  encode image")
>>>>>>> 9e6cbd69f5d46c0db07bee9bbdbaf210cc593855

        if args.write:
            cv2.imwrite(filename, img.frame)
            cv2.waitKey(10)
