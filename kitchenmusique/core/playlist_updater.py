import logging
import sched
import threading
import time

# mpd client throws this when connection fails
from socket import error as SocketError

from mpd import (MPDClient, CommandError)

from kitchenmusique import config, gproxy

from kitchenmusique.core.types import PlaylistUpdateMode


class PlaylistUpdater:
    def __init__(self):
        self.logger = logging.getLogger("kitchenmusique")
        self.providers = []
        self.scheduler = sched.scheduler(time.time, time.sleep)
        self.stop_event = threading.Event()
        self.event_ = None

    def register_providers_from_config(self):
        for desc in config.CONFIG_ENABLED_PROVIDERS:
            self.logger.info("Registered playlist provider: {0} "
                             "(query: '{1}', playlist: '{2}', updatemode: {3}, "
                             "updateinterval: {4} minutes, enqueue: {5})".format(
                                desc.provider.__name__,
                                desc.querystring,
                                desc.playlist,
                                desc.updatemode,
                                desc.updateinterval,
                                desc.enqueue))
            self.register_provider(desc)

    def register_provider(self, provider_desc):
        self.providers.append(provider_desc)

    def update_provider(self, provider_desc):
        client = MPDClient()
        client.timeout = 10
        client.idletimeout = None

        self.logger.info("Updating playlist using provider {0}".format(provider_desc.provider.__name__))

        self.logger.debug("Connecting to MPD at {0}:{1}".format(
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
        self.logger.debug("Client status: {0}".format(client.status()))

        if config.CONFIG_MPD_FORCE_CONSUME_MODE is True and client.status()['consume'] != '1':
            client.consume(1)

        provider = provider_desc.provider()

        if provider_desc.playlist is not None and provider_desc.updatemode == PlaylistUpdateMode.REPLACE:
            try:
                client.playlistclear(provider_desc.playlist)
            # Probably no playlist with that name, let's create it first and ONLY THEN clear it
            except CommandError:
                client.save(provider_desc.playlist)
                client.playlistclear(provider_desc.playlist)

        for entry in provider.get_playlist(provider_desc.querystring):
            albumtracks = gproxy.Request(config.CONFIG_GPROXY_HOST, config.CONFIG_GPROXY_PORT) \
                .search_for_album() \
                .search_by_artist(entry.artist) \
                .search_by_album(entry.album) \
                .get()

            for track in albumtracks:
                if provider_desc.playlist is not None:
                    try:
                        client.playlistadd(provider_desc.playlist, track.url)
                    except CommandError:
                        client.save(provider_desc.playlist)
                        client.playlistclear(provider_desc.playlist)
                        client.playlistadd(provider_desc.playlist, track.url)

                if provider_desc.enqueue:
                    self.logger.info("Enqueuing track '{0}' ({1})".format(track.title, track.url))
                    client.add(track.url)

        self.logger.debug("Current playlist: ")
        for song in client.playlistinfo():
            self.logger.debug(song)

    def __update_provider_sched_wrapper(self, desc):
        try:
            self.update_provider(desc)
        except Exception as e:
            self.logger.error("Failed to update provider '{0}' - {1}!".format(desc.provider.__name__, e))
        finally:
            self.event_ = self.scheduler.enter(
                desc.updateinterval * 60,
                1,
                self.__update_provider_sched_wrapper,
                (desc,))

    def start(self):
        self.logger.debug("PlaylistUpdater -- starting and scheduling next updates...")

        for entry in self.providers:
            try:
                self.update_provider(entry)
            except Exception as e:
                self.logger.error("Failed to update provider '{0}' - {1}!".format(entry.provider.__name__, e))
            finally:
                self.event_ = self.scheduler.enter(
                    entry.updateinterval * 60,
                    1,
                    self.__update_provider_sched_wrapper,
                    (entry,))

        while not self.stop_event.is_set():
            self.scheduler.run(False)
            time.sleep(1)

    def cancel(self):
        self.stop_event.set()
        if self.event_ is not None:
            self.scheduler.cancel(self.event_)
