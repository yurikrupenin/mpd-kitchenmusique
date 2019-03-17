import logging
import multiprocessing
from multiprocessing import Process, Queue

import numpy
import cv2

_queue = None
_server_uri = None

def _rtsp_client_wrapper(framequeue, uri):

    logger = multiprocessing.log_to_stderr(logging.DEBUG)

    logger.info("Starting client...")

    client = cv2.VideoCapture(uri)

    while True:
        if not client.isOpened():
            logger.info("RTSP connection dropped, restarting...")
            client = cv2.VideoCapture(uri)

        ret, img = client.read()

        if ret:
            framequeue.put(img)
        else:
            if not client.isOpened():
                logger.info("Process ended.")
                return


class RtspClient:
    def __init__(self):
        self.process = None
        self.logger = logging.getLogger("kitchenmusique")


    def connect(self, server_uri):
        global _server_uri
        global _queue

        _server_uri = server_uri
        _queue = Queue()

        self.process = Process(target=_rtsp_client_wrapper, args=(_queue, _server_uri))
        self.process.start()


    def get_image(self):
        """" Returns OpenCV image of last received frame from RTSP stream """
        image = None


        count = 0

        while _queue.qsize() > 1:
            image = _queue.get()
            count += 1

        if count > 30:
            self.logger.debug("Big frameskip -- {0} frames!".format(count))

        return image

