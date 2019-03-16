import logging
import requests

# mpd client throws this when connection fails
from socket import error as SocketError
from mpd import (MPDClient, CommandError)

from kitchenmusique import core

import kitchenmusique.config as config

if __name__ == "__main__":
    playlistUpdater = core.PlaylistUpdater()
    logger = logging.getLogger("kitchenmusique")



def main():
    logger.setLevel(logging.DEBUG)

    consoleHandler = logging.StreamHandler()
    logger.addHandler(consoleHandler)

    logger.debug("Kitchenmusique -- starting...")

    playlistUpdater.register_providers_from_config()

    playlistUpdater.update_all()

    logger.info("Kitchenmusique -- exiting successfully")
    return True


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        logger.error("Exiting due to unhandled exception:")
        logger.exception(e)
