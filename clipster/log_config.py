import logging
import logging.handlers
import platform
from pathlib import Path
import os

LEVEL = logging.DEBUG
current_os = platform.system()
# On Linux and Mac use /tmp
LOG_FILE = "/tmp/clipster.log"
if current_os == "Windows":
    LOG_FILE = Path(os.path.expandvars("%TEMP%")) / "clipster.log"

# Setup logging to rotating files of 10MB and console output
log = logging.getLogger("clipster")
log.setLevel(LEVEL)

ch = logging.StreamHandler()

rfh = logging.FileHandler(LOG_FILE)
rfh = logging.handlers.RotatingFileHandler(LOG_FILE, maxBytes=10097152, backupCount=5)

ch.setLevel(LEVEL)
rfh.setLevel(LEVEL)

formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")

ch.setFormatter(formatter)
rfh.setFormatter(formatter)
log.addHandler(ch)
log.addHandler(rfh)
