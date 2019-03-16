import kitchenmusique.providers as providers
from kitchenmusique.core.types import ProviderQuery, PlaylistUpdateMode

CONFIG_GPROXY_HOST = "192.168.1.83"
CONFIG_GPROXY_PORT = 9999

CONFIG_MPD_HOST = "192.168.1.83"
CONFIG_MPD_PORT = 6600
CONFIG_MPD_USE_PASSWORD = False
#CONFIG_MPD_PASSWORD = "hunter2"
CONFIG_MPD_FORCE_CONSUME_MODE = True

CONFIG_ENABLED_PROVIDERS = [
    ProviderQuery(providers.SputnikMusic, "trending", "sputnikmusic-trending", PlaylistUpdateMode.REPLACE, 60, True)
]
