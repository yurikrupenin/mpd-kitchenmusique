from lxml import html
import requests

from kitchenmusique.core.types import AlbumEntry


class LastFM:
    def __init__(self):
        pass

    # Returns list of freshly released albums
    def get_new_releases(self):
        albums = []

        page = requests.get("https://www.last.fm/music/+releases/out-now/popular")
        tree = html.fromstring(page.content)

        for pos in range(1, 20):
            # This lazy Xpath grabs (artist album) tuples from "Trending albums" table.
            # This will probably break after slightest redesign, but hey it works for now.
            albums.append(AlbumEntry(
                tree.xpath(
                    "(//p[@class='album-grid-item-artist'])[{0}]/span/a/text()".format(pos))[0],
                tree.xpath(
                     "(//h3[@class='album-grid-item-title'])[{0}]/a/text()".format(pos))[0]
            ))

        return list(filter(lambda entry: len(entry.artist) > 0 and len(entry.album) > 0, albums))

    def get_playlist(self, querystring):
        return {
           "new": self.get_new_releases()
        }[querystring]

