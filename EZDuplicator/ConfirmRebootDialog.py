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


class ConfirmRebootDialog(Gtk.Dialog):
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
                    'ConfirmRebootDialog',
                    'ConfirmRebootDialog_Cancel',
                    'ConfirmRebootDialog_Confirm',
                ]
            )
        except Exception as ex:
            logging.error(ex)
            sys.exit(1)

        # Get gui objects
        self.ConfirmRebootDialog = self.builder.get_object('ConfirmRebootDialog')
        self.ConfirmRebootDialog_Cancel = self.builder.get_object('ConfirmRebootDialog_Cancel')
        self.ConfirmRebootDialog_Confirm = self.builder.get_object('ConfirmRebootDialog_Confirm')
        self.ConfirmRebootDialog.show_all()
        self.ConfirmRebootDialog.set_transient_for(parent)
        self.builder.connect_signals(self)

    def on_ConfirmRebootDialog_Cancel_clicked(self, widget, user_data=None):
        """ Handler for ConfirmRebootDialog_Cancel.clicked. """
        self.ConfirmRebootDialog.destroy()

    def on_ConfirmRebootDialog_Confirm_clicked(self, widget, user_data=None):
        """ Handler for ConfirmRebootDialog_Confirm.clicked. """
        self.ConfirmRebootDialog.destroy()
        os.system("sudo reboot")
