#!/bin/python3.9
"""

Copyright (c) 2021 Connor McMillan <connor@mcmillan.website>. All rights reserved.

This work is licensed under the terms of the MIT license.
For a copy, see <https://opensource.org/licenses/MIT>.

"""
import logging
import os
import signal

import sys
from elevate import elevate


def main(argv):
    try:
        """ Ask to levitate """
        elevate(graphical=False)
        """ Kill the app """
        for pid in argv[1:]:
            pid = int(pid)
            os.kill(pid, signal.SIGTERM)
        """ Start the app as a daemon """
        """ Currently /usr/local/bin/ezduplicator-kiosk has `EZDuplicator' on a infinite while true loop which 
            THis means that the following os.system() is not needed as this will result in two instances of
            EZDuplicator. """
        # os.system("/usr/local/bin/EZDuplicator &")
        exit(0)
    except Exception as ex:
        logging.exception(ex)
        exit(1)


if __name__ == '__main__':
    mainret = main(sys.argv) # noqa
    sys.exit(mainret)
