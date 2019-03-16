import logging

# mpd client throws this when connection fails
from socket import error as SocketError

from mpd import (MPDClient, CommandError)

from kitchenmusique import config, gproxy

class PlaylistUpdater:

    def __init__(self):
        self.logger = logging.getLogger("kitchenmusique")
        self.providers = []


    def register_providers_from_config(self):
        for desc in config.CONFIG_ENABLED_PROVIDERS:
            self.logger.info("Registered playlist provider: {0} "\
                            "(query: '{1}', playlist: '{2}', updatemode: {3}, "\
                            "updateinterval: {4} minutes, enqueue: {5})".format(\
                                desc.provider.__name__,
                                desc.querystring,
                                desc.playlist,
                                desc.updatemode,
                                desc.updateinterval,
                                desc.enqueue))
            self.register_provider(desc)

    def register_provider(self, providerDesc):
        self.providers.append(providerDesc)


    def update_provider(self, providerDesc):
        client = MPDClient()
        client.timeout = 10
        client.ideltimeout = None

        self.logger.info("Updating playlist using provider {0}".format(providerDesc.provider.__name__))

        self.logger.debug("Connecting to MPD at {0}:{1}".format(\
            config.CONFIG_MPD_HOST,
            config.CONFIG_MPD_PORT))

        # connect to MPD
        try:
            client.connect(config.CONFIG_MPD_HOST, config.CONFIG_MPD_PORT)
        except SocketError:
            self.logger.error("MPD connection failed, exiting")
            return False

        # authenticate if we have password enabled
        if config.CONFIG_MPD_USE_PASSWORD:
            try:
                client.password(config.CONFIG_MPD_PASSWORD)
            except CommandError:
                self.logger.error("MPD password authentication failed, exiting")
                return False

        self.logger.debug("Connected to MPD; version: {0}".format(client.mpd_version))

        f = client.status()
        print(f)
        if client.status()['state'] != 'play':
            client.clear()

        provider = providerDesc.provider()
        for entry in provider.get_playlist(providerDesc.querystring):
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

    def update_all(self):
        for entry in self.providers:
            self.update_provider(entry)
