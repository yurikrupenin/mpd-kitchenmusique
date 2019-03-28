import logging
import multiprocessing as mp
import threading
import time

import cv2

from kitchenmusique import config

_queue = None
_heartbeat_queue = None


def _rtsp_client_wrapper(framequeue, heartbeatqueue, uri):
    logger = mp.log_to_stderr(logging.DEBUG)

    logger.info("Starting RTSP client...")

    client = cv2.VideoCapture(uri)

    last_active = time.time()
    heartbeatqueue.put(last_active)

    while True:
        if not client.isOpened():
            logger.info("RTSP connection dropped, reestablishing...")
            time.sleep(1)
            client = cv2.VideoCapture(uri)

        ret, img = client.read()

        if ret:
            if time.time() - last_active > config.CONFIG_RTSP_HEARTBEAT_INTERVAL:
                last_active = time.time()
                heartbeatqueue.put(last_active)

            if framequeue.qsize() < 2:
                framequeue.put(img)


class RtspClient:
    def __init__(self):
        self.process = None
        self.monitor_thread = None
        self.server_uri = None
        self.stop_event = threading.Event()
        self.logger = logging.getLogger("kitchenmusique")

    def _monitor_heartbeat(self):
        global _queue
        global _heartbeat_queue

        last_heartbeat = time.time()

        while not (self.stop_event.is_set()):
            time.sleep(1)
            while _heartbeat_queue.qsize() > 0:
                last_heartbeat = _heartbeat_queue.get()

            if time.time() - last_heartbeat >= config.CONFIG_RTSP_HEARTBEAT_PANIC:
                self.logger.warning("RTSP client heartbeat missed, restarting...")
                self.process.terminate()
                self.logger.info("RTSP process terminated.")
                self.process.join()

                self.connect(self.server_uri)

                self.logger.info("RTSP child process restarted.")
                last_heartbeat = time.time()

    def connect(self, server_uri):
        global _queue
        global _heartbeat_queue

        self.server_uri = server_uri

        if _queue is not None:
            _queue.close()

        if _heartbeat_queue is not None:
            _heartbeat_queue.close()

        _queue = mp.Queue()
        _heartbeat_queue = mp.Queue()

        self.process = mp.Process(target=_rtsp_client_wrapper, args=(_queue, _heartbeat_queue, self.server_uri))
        self.process.start()

        if self.monitor_thread is None:
            self.monitor_thread = threading.Thread(target=self._monitor_heartbeat, args=())
            self.monitor_thread.start()

    def get_image(self):
        """ Returns OpenCV image of last received frame from RTSP stream """
        """ Returns None if read failed """
        global _queue
        image = None

        try:
            image = _queue.get_nowait()

            if _queue.qsize() > 2:
                self.logger.warning("RTSP: {0} unprocessed frames in queue!".format(_queue.qsize()))

        except Exception as e:
            image = None
            self.logger.debug("RTSP: Exception during image read op!")

        finally:
            return image

        # Should be unreachable
        return None

    def terminate(self):
        self.logger.debug("RTSP client: terminating heartbeat monitor thread...")
        self.stop_event.set()
        self.monitor_thread.join()
        self.logger.debug("Done.")

        self.logger.debug("RTSP client: terminating child process...")
        self.process.terminate()
        self.process.join()
        self.logger.debug("Done.")

