from kitchenmusique import providers
from kitchenmusique.core.types import ProviderQuery, PlaylistUpdateMode

# If there's nobody in the video feed for 3 minutes, the music will stop playing
CONFIG_DEACTIVATION_TIME = 3 * 60

# Google Play Music Proxy parameters, you should configure it and make sure it works before running Kitchenmusique
CONFIG_GPROXY_HOST = "192.168.1.110"
CONFIG_GPROXY_PORT = 9999

# MPD connection parameters
CONFIG_MPD_HOST = "192.168.1.110"
CONFIG_MPD_PORT = 6600

# Set to true and uncomment next string if you're using authentication on your MPD server
CONFIG_MPD_USE_PASSWORD = False
CONFIG_MPD_PASSWORD = "hunter2"

# Enable MPD's consume mode when playing music
CONFIG_MPD_FORCE_CONSUME_MODE = True

# RTSP stream URL
CONFIG_RTSP_URL = "rtsp://192.168.1.100:8554/unicast"

# Sigh, we need this because our RTSP client isn't very stable and sometimes we may need to restart it.
CONFIG_RTSP_HEARTBEAT_INTERVAL = 3
CONFIG_RTSP_HEARTBEAT_PANIC = 20


# Default configuration enables SputnikMusic provider, fetches trending albums, and places
# Google Play Music playlist for them into MPD playlist "sputnikmusic-trending", replacing old content.
# This happens once a day (24 * 60 minutes), each time appending the default MPD queue (last "True" in parameter list)
CONFIG_ENABLED_PROVIDERS = [
    ProviderQuery(providers.SputnikMusic,
                  "trending",
                  "sputnikmusic-trending",
                  PlaylistUpdateMode.REPLACE,
                  24 * 60,
                  True)
]

# Object detection model parameters
CONFIG_YOLO_CFG_FILE = "yolo/yolov3-tiny.cfg"
CONFIG_YOLO_WEIGHTS_FILE = "yolo/yolov3-tiny.weights"
CONFIG_YOLO_CLASSES_FILE = "yolo/yolov3-classes.txt"

# Defines which object classes detection should instruct Kitchenmusique to enable MPD playback.
# See CONFIG_YOLO_CLASSES_FILE for full list of available variants.
CONFIG_YOLO_TRIGGER_CLASSES = ["person"]

# How confident the model should be that there's a person in the video feed before we enable music
CONFIG_YOLO_CONFIDENCE_THRESHOLD = 0.1
