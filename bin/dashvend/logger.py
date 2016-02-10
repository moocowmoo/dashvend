import logging
import os
import sys

from config import DASHVEND_DIR

LOGFILE = os.path.join(DASHVEND_DIR, 'dashvend.log')
LEVEL = logging.DEBUG

log = logging.getLogger('')
log.setLevel(LEVEL)
format = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")

ch = logging.StreamHandler(sys.stdout)
ch.setFormatter(format)
log.addHandler(ch)

fh = logging.FileHandler(LOGFILE)
fh.setFormatter(format)
log.addHandler(fh)


def debug(msg):
    log.debug(msg)


def warn(msg):
    log.warn(msg)


def info(msg):
    log.info(msg)
