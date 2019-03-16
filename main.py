import logging
import requests

# mpd client throws this when connection fails
from socket import error as SocketError
from mpd import (MPDClient, CommandError)

from kitchenmusique import core, gproxy, providers

import kitchenmusique.config as config

if __name__ == "__main__":
    playlistUpdater = core.PlaylistUpdater()
    logger = logging.getLogger("kitchenmusique")


def init_providers():
    for item in config.providers:
        playlistUpdater.register_provider(item)


def main():
    logger.setLevel(logging.DEBUG)

    consoleHandler = logging.StreamHandler()
    logger.addHandler(consoleHandler)

    logger.debug("Kitchenmusique -- starting...")

    client = MPDClient()
    client.timeout = 10
    client.ideltimeout = None

    # connect to MPD
    try:
        client.connect(config.CONFIG_MPD_HOST, config.CONFIG_MPD_PORT)
    except SocketError:
        logger.error("MPD connection failed, exiting")
        return False

    # authenticate if we have password enabled
    if config.CONFIG_MPD_USE_PASSWORD:
        try:
            client.password(config.CONFIG_MPD_PASSWORD)
        except CommandError:
            logger.error("MPD password authentication failed, exiting")
            return False

    print("MPD version: {0}".format(client.mpd_version))

    f = client.status()
    print(f)
    if client.status()['state'] != 'play':
        client.clear()

    for entry in providers.SputnikMusic().get_trending_albums():
        albumtracks = gproxy.Request(config.CONFIG_GPROXY_HOST, config.CONFIG_GPROXY_PORT) \
            .search_for_album() \
            .search_by_artist(entry.artist) \
            .search_by_album(entry.album) \
            .get()

        for track in albumtracks:
            print("{0} ({1})".format(track.title, track.url))
            client.add(track.url)

    if client.status()['state'] != 'play':
        client.play()

    for song in client.playlistinfo():
        print(song)

    logger.info("Kitchenmusique -- exiting successfully")
    return True


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        logger.error("Exiting due to unhandled exception:")
        logger.exception(e)
