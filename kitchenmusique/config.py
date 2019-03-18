import kitchenmusique.providers as providers
from kitchenmusique.core.types import ProviderQuery, PlaylistUpdateMode

# If there's nobody in the video feed for 1 minute, the music will stop playing
CONFIG_DEACTIVATION_TIME = 60

CONFIG_GPROXY_HOST = "192.168.1.110"
CONFIG_GPROXY_PORT = 9999

CONFIG_MPD_HOST = "192.168.1.110"
CONFIG_MPD_PORT = 6600
CONFIG_MPD_USE_PASSWORD = False
#CONFIG_MPD_PASSWORD = "hunter2"
CONFIG_MPD_FORCE_CONSUME_MODE = True

CONFIG_RTSP_URL = "rtsp://192.168.1.100:8554/unicast"
CONFIG_RTSP_HEARTBEAT_INTERVAL = 3
CONFIG_RTSP_HEARTBEAT_PANIC = 20

CONFIG_ENABLED_PROVIDERS = [
    ProviderQuery(providers.SputnikMusic, "trending", "sputnikmusic-trending", PlaylistUpdateMode.REPLACE, 60, True)
]

# Object detection model parameters
CONFIG_YOLO_CFG_FILE = "yolo/yolov3-tiny.cfg"
CONFIG_YOLO_WEIGHTS_FILE = "yolo/yolov3-tiny.weights"
CONFIG_YOLO_CLASSES_FILE = "yolo/yolov3-classes.txt"

# Defines which object classes detection should instruct Kitchenmusique to enable MPD playback.
# See CONFIG_YOLO_CLASSES_FILE for full list of available variants.
CONFIG_YOLO_TRIGGER_CLASSES = ["person"]


CONFIG_YOLO_CONFIDENCE_THRESHOLD = 0.0