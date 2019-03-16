from enum import Enum

import requests
import urllib3

from kitchenmusique.gproxy.m3u_parser import M3uParser


class RequestType(Enum):
    SEARCH = 1
    UNDEFINED = 0xFFFFFFFF

class InvalidRequestType(Exception):
    pass

class ConnectionError(Exception):
    pass



class Request:
    def __init__(self, host, port = 9999):
        self.requestType = RequestType.UNDEFINED
        self.hostUrl = "http://{0}:{1}".format(host, port)

        self.params = {
        }

    def search_for_album(self):
        self.requestType = RequestType.SEARCH
        self.params.update({"type" : "album"})
        return self

    def search_for_match(self):
        self.requestType = RequestType.SEARCH
        self.params.update({"type" : "match"})
        return self

    def search_by_artist(self, artistName):
        self.params.update({"artist" : artistName})
        return self

    def search_by_album(self, albumName):
        self.params.update({"title" : albumName})
        return self

    def get(self):
        try:
            requestString = self.__request_string(self.requestType)
        except KeyError:
            raise InvalidRequestType("Invalid request type")

        try:
            # {0} is a host URL, {1} is a command, and {2} is a standard HTTP request
            # query string ("?type=match&artist=Vektor&title=Terminal%20Redux")
            req = requests.get("{0}/{1}".format(self.hostUrl, requestString), params = self.params)
        except requests.exceptions.ConnectionError as e:
            # That's pretty ugly, but long story short GMusicProxy just kinda aborts the connection
            # if there's nothing to return, and python's requests library doesn't really
            # differentiate between a connection which was dropped and a connection which
            # was never even established. So we're taking a deep breath and assuming
            # that a dropped connection is perfectly fine, it's just that search didn't return
            # any results, that's all.
            if type(e.__context__) == urllib3.exceptions.ProtocolError:
                return []
            else:
                raise ConnectionError


        return M3uParser(req.text).tracklist()


    def __request_string(self, reqtype):
        return {
           RequestType.SEARCH : "get_by_search"
        }[reqtype]

