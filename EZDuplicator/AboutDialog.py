"""

Copyright (c) 2021 Connor McMillan <connor@mcmillan.website>. All rights reserved.

This work is licensed under the terms of the MIT license.
For a copy, see <https://opensource.org/licenses/MIT>.

"""
import logging
import os
import sys
from pathlib import Path

from gi import require_version as gi_require_version

import EZDuplicator.version
import EZDuplicator.lib.EZDuplicator

gi_require_version('Gtk', '3.0')
from gi.repository import Gtk


class AboutDialog(Gtk.AboutDialog):
    """ Main window with all components. """

    def __init__(self, parent):
        Gtk.AboutDialog.__init__(self)
        self.builder = Gtk.Builder()
        gladefile = str(Path(__file__).parent.absolute()) + '/res/window.ui'
        if not os.path.exists(gladefile):
            # Look for glade file in this project's directory.
            gladefile = os.path.join(sys.path[0], gladefile)

        try:
            self.builder.add_objects_from_file(
                gladefile,
                [
                    'AboutDialog',
                    'AboutDialog_ServiceTag',
                ]
            )
        except Exception as ex:
            logging.error(ex)
            sys.exit(1)

        # Get gui objects
        self.AboutDialog = self.builder.get_object('AboutDialog')
        self.version = EZDuplicator.version.__version__
        self.AboutDialog.set_property("version", str(self.version))
        self.AboutDialog_ServiceTag = self.builder.get_object('AboutDialog_ServiceTag')
        self.AboutDialog_ServiceTag.set_text(EZDuplicator.lib.EZDuplicator.get_serial_number())
        self.AboutDialog.show_all()
        self.AboutDialog.set_transient_for(parent)
        self.builder.connect_signals(self)
