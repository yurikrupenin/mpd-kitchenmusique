from lxml import html
import requests

from kitchenmusique.core.types import AlbumEntry

class SputnikMusic:

    def __init__(self):
        self.albumlist = []

        page = requests.get("https://sputnikmusic.com")
        self.tree = html.fromstring(page.content)

        albums = []

        for pos in range(1, 16):
            # This lazy Xpath grabs (artist album) tuples from "Trending albums" table.
            # This will probably break after slightest redesign, but hey it works for now.
            albums.append(AlbumEntry(
                 self.tree.xpath("/html/body/table/tr[3]/td/table/tr[1]/td[3]/table/tr[2]/td/table/tr[{0}]/td[1]/a/font/text()".format(pos))[0],
                 self.tree.xpath("/html/body/table/tr[3]/td/table/tr[1]/td[3]/table/tr[2]/td/table/tr[{0}]/td[1]/a/font/span/text()".format(pos))[0]
            ))

        self.albumlist = list(filter(
            lambda entry:
                len(entry.artist) > 0 and len(entry.album) > 0,
            albums))
               

    # Returns list of albums in "Trending albums" category
    def get_trending_albums(self):
        return self.albumlist

    def get_playlist(self, querystring):
        return {
           "trending": self.get_trending_albums()
        }[querystring]

