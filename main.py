import logging
import threading


from kitchenmusique import core, detect


if __name__ == "__main__":
    playlistUpdater = core.PlaylistUpdater()
    logger = logging.getLogger("kitchenmusique")



def main():
    logger.setLevel(logging.DEBUG)

    consoleHandler = logging.StreamHandler()
    logger.addHandler(consoleHandler)

    logger.debug("Kitchenmusique -- starting...")


    playlistUpdater.register_providers_from_config()
    playlistThread = threading.Thread(target = playlistUpdater.start)
    playlistThread.start()

    neuralNet = detect.PersonDetector()

    rtspClient = detect.RtspClient()
    rtspClient.connect("rtsp://192.168.1.100:8554/unicast")

    while True:
        image = rtspClient.get_image()

        if image is None:
            continue

        neuralNet.visualize(image)



    logger.info("Kitchenmusique -- exiting successfully")
    return True


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        logger.error("Exiting due to unhandled exception:")
        logger.exception(e)
