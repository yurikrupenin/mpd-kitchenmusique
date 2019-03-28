import logging
import sys
import threading
import time

# mpd client throws this when connection fails
from socket import error as SocketError

from mpd import (MPDClient, CommandError)


from kitchenmusique import core, config, detect


if __name__ == "__main__":
    playlistUpdater = core.PlaylistUpdater()
    playlistThread= threading.Thread(target=playlistUpdater.start)
    rtspClient = None
    logger = logging.getLogger("kitchenmusique")


def exit_handler():
    global rtspClient
    global logger

    if rtspClient is not None:
        logger.debug("Exit handler: terminating RTSP client")
        rtspClient.terminate()
    else:
        logger.debug("Exit handler: RTSP client isn't even initialized - nothing to terminate!")

    if playlistThread is not None:
        logger.debug("Exit handler: killing playlist updater...")
        playlistUpdater.cancel()
        playlistThread.join()
        logger.debug("Done!")

    logger.debug("Exit handler: everything's done!")

def main():
    global rtspClient
    global playlistUpdater
    global logger

    triggered = False
    last_triggered = time.time()

    logger.setLevel(logging.DEBUG)

    console_handler = logging.StreamHandler()
    logger.addHandler(console_handler)

    logger.debug("Kitchenmusique -- starting...")

    playlistUpdater.register_providers_from_config()

    playlistThread.start()

    neural_net = detect.PersonDetector()

    rtspClient = detect.RtspClient()
    rtspClient.connect(config.CONFIG_RTSP_URL)

    while True:
        try:
            image = rtspClient.get_image()

            if image is None:
                time.sleep(0.3)
                continue

            descriptions = neural_net.process(image, False)
        except Exception:
            continue

        matches = list(filter(lambda x: x.classid in config.CONFIG_YOLO_TRIGGER_CLASSES, descriptions))
        accepted = list(filter(lambda x: x.confidence > config.CONFIG_YOLO_CONFIDENCE_THRESHOLD, matches))

        if len(accepted) > 0:
            logger.info("Trigger class presence detected!")

            last_triggered = time.time()

            if not triggered:
                triggered = True
                client = MPDClient()
                client.timeout = 10
                client.idletimeout = None

                logger.debug("Connecting to MPD at {0}:{1}".format(
                    config.CONFIG_MPD_HOST,
                    config.CONFIG_MPD_PORT))

                # connect to MPD
                try:
                    client.connect(config.CONFIG_MPD_HOST, config.CONFIG_MPD_PORT)
                except SocketError:
                    logger.error("MPD connection failed")

                # authenticate if we have password enabled
                if config.CONFIG_MPD_USE_PASSWORD:
                    try:
                        client.password(config.CONFIG_MPD_PASSWORD)
                    except CommandError:
                        logger.error("MPD password authentication failed, exiting")

                # finally, play music
                if client.status()['state'] != 'play':
                    client.play()

        elif triggered and time.time() - last_triggered > config.CONFIG_DEACTIVATION_TIME:
            triggered = False
            client = MPDClient()
            client.timeout = 10
            client.idletimeout = None

            logger.debug("Connecting to MPD at {0}:{1}".format(
                config.CONFIG_MPD_HOST,
                config.CONFIG_MPD_PORT))

            # connect to MPD
            try:
                client.connect(config.CONFIG_MPD_HOST, config.CONFIG_MPD_PORT)
            except SocketError:
                logger.error("MPD connection failed")

            # authenticate if we have password enabled
            if config.CONFIG_MPD_USE_PASSWORD:
                try:
                    client.password(config.CONFIG_MPD_PASSWORD)
                except CommandError:
                    logger.error("MPD password authentication failed, exiting")

            if client.status()['state'] == 'play':
                client.stop()

    logger.info("Kitchenmusique -- exiting successfully")
    exit_handler()
    return True


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        exit_handler()
        sys.exit(0)
    except Exception as e:
        logger.error("Exiting due to unhandled exception:")
        logger.exception(e)
