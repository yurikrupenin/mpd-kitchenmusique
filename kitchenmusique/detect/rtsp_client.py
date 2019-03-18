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
            if _queue.qsize() < 2:
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


        image = _queue.get()

        if _queue.qsize() > 2:
            self.logger.warning("RTSP: {0} unprocessed frames in queue!".format(_queue.qsize()))


        return image

