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

import EZDuplicator.Connect2HubDialog

gi_require_version('Gtk', '3.0')

from gi.repository import Gtk


class PowerOnHubDialog(Gtk.Dialog):
    """ Main window with all components. """

    def __init__(self, option):
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
                    'PowerOnHubDialog',
                    'PowerOnHubDialog_CancelButton',
                    'PowerOnHubDialog_ContinueButton',
                ]
            )
        except Exception as ex:
            logging.error(ex)
            sys.exit(1)

        # Get gui objects
        self.PowerOnHubDialog = self.builder.get_object('PowerOnHubDialog')
        self.PowerOnHubDialog_CancelButton = self.builder.get_object('PowerOnHubDialog_CancelButton')
        self.PowerOnHubDialog_ContinueButton = self.builder.get_object('PowerOnHubDialog_ContinueButton')
        self.PowerOnHubDialog.show_all()
        self.builder.connect_signals(self)
        self.option = option

    def on_PowerOnHubDialog_CancelButton_clicked(self, widget, user_data=None):
        """ Handler for PowerOnHubDialog_CancelButton.clicked. """
        self.PowerOnHubDialog.destroy()

    def on_PowerOnHubDialog_ContinueButton_clicked(self, widget, user_data=None):
        """ Handler for PowerOnHubDialog_ContinueButton.clicked. """
        EZDuplicator.Connect2HubDialog.Connect2HubDialog(self.option)
        self.PowerOnHubDialog.destroy()
