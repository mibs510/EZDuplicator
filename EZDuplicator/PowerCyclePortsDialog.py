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

gi_require_version('Gtk', '3.0')

from gi.repository import Gtk


class PowerCyclePortsDialog(Gtk.Dialog):
    """ Main window with all components. """

    def __init__(self, parent):
        Gtk.Dialog.__init__(self)
        self.builder = Gtk.Builder()
        gladefile = str(Path(__file__).parent.absolute()) + '/res/window.ui'
        if not os.path.exists(gladefile):
            # Look for glade file in this project's directory.
            gladefile = os.path.join(sys.path[0], gladefile)

        try:
            self.builder.add_objects_from_file(
                gladefile,
                [
                    'PowerCyclePortsDialog',
                    'PowerCyclePortsDialog_ContinueButton',
                ]
            )
        except Exception as ex:
            logging.exception(ex)
            sys.exit(1)

        # Get gui objects
        self.PowerCyclePortsDialog = self.builder.get_object('PowerCyclePortsDialog')
        self.PowerCyclePortsDialog_ContinueButton = self.builder.get_object('PowerCyclePortsDialog_ContinueButton')
        self.builder.connect_signals(self)
        self.PowerCyclePortsDialog.show_all()
        self.PowerCyclePortsDialog.set_transient_for(parent)

    def on_PowerCyclePortsDialog_ContinueButton_clicked(self, widget, user_data=None):
        """ Handler for PowerCyclePortsDialog_ContinueButton.clicked. """
        self.PowerCyclePortsDialog.destroy()
