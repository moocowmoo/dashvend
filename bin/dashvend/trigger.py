"""
sale trigger (invokes setuid relay toggle)
"""

import os
import subprocess
from config import DASHVEND_DIR
from logger import info


class Trigger(object):

    def __init__(self):
        pass

    def trigger(self):
        info("    -----------------------------")
        info("    SALE --> TRIGGERING RELAYS")
        info("    -----------------------------")
        subprocess.call(os.path.join(DASHVEND_DIR, 'bin', 'trigger_relay'))
