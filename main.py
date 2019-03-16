import logging
from kitchenmusique import core


if __name__ == "__main__":
    playlistUpdater = core.PlaylistUpdater()
    logger = logging.getLogger("kitchenmusique")



def main():
    logger.setLevel(logging.DEBUG)

    consoleHandler = logging.StreamHandler()
    logger.addHandler(consoleHandler)

    logger.debug("Kitchenmusique -- starting...")

    playlistUpdater.register_providers_from_config()

    playlistUpdater.start()

    logger.info("Kitchenmusique -- exiting successfully")
    return True


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        logger.error("Exiting due to unhandled exception:")
        logger.exception(e)
