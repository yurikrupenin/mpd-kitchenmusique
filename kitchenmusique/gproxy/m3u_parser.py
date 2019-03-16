from collections import namedtuple

PlaylistEntry = namedtuple("PlaylistEntry", "title length url")


class M3uParser:

    def __init__(self, text):
        self.lines = text.splitlines()
        self.tracks = []
        self.__parse()


    def tracklist(self):
        return self.tracks

    def __parse(self):
        length = len(self.lines)

        trackinfo = None
        url = None

        for pos in range(length):
            line = self.lines[pos]

            if line.startswith("#EXTM3U"):
                continue
                
            lineparts = line.split(u'#EXTINF:')
            if len(lineparts) == 2:
                trackinfo = lineparts[1]
            else:
                url = line
            
            if trackinfo != None and url != None:
                trackinfo = trackinfo.split(',')

                if len(trackinfo) >= 2:
                    length = int(trackinfo[0])
                    title = trackinfo[1]

                    self.tracks.append(PlaylistEntry(title, length, url))
                    trackinfo = None
                    url = None
