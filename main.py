import requests

from mpd import MPDClient

import gproxy
import providers

import config



if __name__ == "__main__":

    client = MPDClient()
    client.timeout = 10
    client.ideltimeout = None
    client.connect(config.CONFIG_MPD_HOST, config.CONFIG_MPD_PORT)
    print("MPD version: {0}".format(client.mpd_version))
    client.clear()

    for entry in providers.SputnikMusic().get_albums():
        albumtracks = gproxy.Request(config.CONFIG_GPROXY_HOST, config.CONFIG_GPROXY_PORT)\
            .search_for_album()\
            .search_by_artist(entry.artist)\
            .search_by_album(entry.album)\
            .get()
        
        for track in albumtracks:
            print("{0} ({1})".format(track.title, track.url))
            client.add(track.url)

    client.play()

    for song in client.playlistinfo():
        print(song)

