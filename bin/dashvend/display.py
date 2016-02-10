"""
vending display driver - bash script wrapper
"""

import os
from config import DASHVEND_DIR

# bash script for displaying screen updates
SCREEN_DRIVER_SCRIPT = os.path.join(DASHVEND_DIR,
                                    'bin', 'show_screen_number.sh')


class Display(object):

    def __init__(self):
        return

    def show_screen_number(self, number, address=None, amount=None):
        if str(number).isdigit():
            os.system(SCREEN_DRIVER_SCRIPT + " %s %s %s" %
                      (number, address, amount))
