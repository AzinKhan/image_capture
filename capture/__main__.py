import logging
import argparse
from multiprocessing import Process, Queue

from capture import MotionDetector, getTime, send_image

logging.basicConfig(level=logging.INFO, format="[%(asctime)s] %(message)s")

logger = logging.getLogger()

parser = argparse.ArgumentParser(description="A simple motion detector")
parser.add_argument(
    "--threshold",
    metavar="threshold",
    type=float,
    default=10,
    nargs="?",
    help="Threshold for motion detection.",
)
parser.add_argument(
    "--width", metavar="width", type=int, default=1280, nargs="?", help="Width of image"
)
parser.add_argument(
    "--height",
    metavar="height",
    type=int,
    default=960,
    nargs="?",
    help="Height of image",
)
parser.add_argument(
    "--cam", metavar="cam", type=int, default=0, nargs="?", help="Camera ID"
)
parser.add_argument("--show", action="store_true", help="Show images")
parser.add_argument("--write", action="store_true", help="Write images to file")
parser.add_argument(
    "--send", action="store_true", help="Upload images to remote server"
)
parser.add_argument(
    "--url",
    metavar="url",
    type=str,
    default="http://0.0.0.0:8000/",
    nargs="?",
    help="Remote URL",
)
parser.add_argument("--verbose", "-v", action="store_true", help="Allow debug logs.")
args = parser.parse_args()
if args.verbose:
    logger.setLevel(logging.DEBUG)

detector = MotionDetector(
    cam_num=args.cam, thresh=args.threshold, width=args.width, height=args.height
)

if args.send:
    info_queue = Queue()
    sender = Process(target=send_image, args=(info_queue,))
    sender.daemon = True
    sender.start()

running = True
while running:
    try:
        for img in detector.run():
            if args.show:
                img.show("Motion")

            filename = getTime() + ".jpg"
            if args.send:
                encoded = img.encode()
                if encoded:
                    info_queue.put((args.url, encoded, filename))
                else:
                    logger.error("Could not encode image")

            if args.write:
                img.write(filename)
    except KeyboardInterrupt:
        logger.info("Stopping processes...")
        if args.send:
            sender.terminate()
            sender.join()
        logger.info("All processes stopped.")
        running = False
