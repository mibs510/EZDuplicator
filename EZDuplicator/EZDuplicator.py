#!/usr/bin/env python3
"""

Copyright (c) 2021 Connor McMillan <connor@mcmillan.website>. All rights reserved.

This work is licensed under the terms of the MIT license.
For a copy, see <https://opensource.org/licenses/MIT>.

"""
import argparse
import logging
import sys

from elevate import elevate
from gi import require_version as gi_require_version

import EZDuplicator.App
import EZDuplicator.version
import EZDuplicator.lib.EZDuplicator

gi_require_version('Gtk', '3.0')

from gi.repository import Gtk


def main():
    elevate(graphical=False)
    try:
        parser = argparse.ArgumentParser(prog="EZDuplicator",
                                         formatter_class=argparse.RawTextHelpFormatter,
                                         epilog="EZDuplicator v{}\n"
                                                "(c) 2021 Connor McMillan "
                                                "<connor@mcmillan.website>".format(EZDuplicator.version.__version__))
        parser.add_argument('-d', '--debug', help='Disable 12VPM and other non-essentials.',
                            action='store_true')
        args = parser.parse_args()
        """ Main entry point for the program. """
        EZDuplicator.lib.EZDuplicator.create_default_config()
        EZDuplicator.lib.EZDuplicator.improve_software()
        EZDuplicator.lib.EZDuplicator.init_logging()
        if args.debug:
            logging.info("Debug mode activated.")
            app = EZDuplicator.App.App(debug=True)  # noqa
        else:
            app = EZDuplicator.App.App() # noqa
        return Gtk.main()
    except Exception as ex:
        logging.exception(ex)


if __name__ == '__main__':
    mainret = main()
    sys.exit(mainret)
