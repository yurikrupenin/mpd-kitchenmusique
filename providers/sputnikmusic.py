from lxml import html
import requests

from collections import namedtuple

AlbumEntry = namedtuple("AlbumEntry", "artist album")


class SputnikMusic:

    def __init__(self):
        self.albumlist = []

        page = requests.get("https://sputnikmusic.com")
        self.tree = html.fromstring(page.content)

        for pos in range(1, 26):
            self.albumlist.append(AlbumEntry(\
                 self.tree.xpath("/html/body/table/tr[3]/td/table/tr[1]/td[3]/table/tr[2]/td/table/tr[{0}]/td[1]/a/font/text()".format(pos)),
                 self.tree.xpath("/html/body/table/tr[3]/td/table/tr[1]/td[3]/table/tr[2]/td/table/tr[{0}]/td[1]/a/font/span/text()".format(pos))
                ))

        self.albumlist = list(filter(\
            lambda entry:
                len(entry.artist) > 0 and len(entry.album) > 0,\
            self.albumlist))
               

    def get_albums(self):
        return self.albumlist

