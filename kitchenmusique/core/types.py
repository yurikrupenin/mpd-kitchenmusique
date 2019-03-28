from collections import namedtuple
from enum import Enum

AlbumEntry = namedtuple("AlbumEntry", "artist album")

ProviderQuery = namedtuple("ProviderQuery", "provider querystring playlist updatemode updateinterval enqueue")

DetectedObject = namedtuple("DetectedObject", "classid confidence")


class PlaylistUpdateMode(Enum):
    APPEND = 1
    REPLACE = 2

