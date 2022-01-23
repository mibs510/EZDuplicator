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

import EZDuplicator.ConsentDialog
import EZDuplicator.NoInternetDialog
import EZDuplicator.lib.EZDuplicator

gi_require_version('Gtk', '3.0')

from gi.repository import Gtk


class AppCrashedDialog(Gtk.Dialog):
    """ Main window with all components. """

    def __init__(self):
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
                    'AppCrashedDialog',
                    'AppCrashedDialog_Reboot',
                    'SendLogs_Button',
                ]
            )
        except Exception as ex:
            logging.error(ex)
            sys.exit(1)

        # Get gui objects
        self.AppCrashedDialog = self.builder.get_object('AppCrashedDialog')
        self.AppCrashedDialog_Reboot = self.builder.get_object('AppCrashedDialog_Reboot')
        self.SendLogs_Button = self.builder.get_object('SendLogs_Button')
        self.builder.connect_signals(self)
        self.AppCrashedDialog.show_all()

    def on_AppCrashedDialog_Reboot_clicked(self, widget, user_data=None):
        """ Handler for AppCrashedDialog_Reboot.clicked. """
        self.AppCrashedDialog.destroy()
        os.system("sudo reboot")

    def on_SendLogs_Button_clicked(self, widget, user_data=None):
        """ Handler for SendLogs_Button.clicked. """
        if EZDuplicator.lib.EZDuplicator.has_internet_connection():
            logging.debug("Detected a valid internet connection")
            EZDuplicator.ConsentDialog.ConsentDialog()
        else:
            logging.debug("Failed to detect a valid internet connection")
            EZDuplicator.NoInternetDialog.NoInternetDialog(self.AppCrashedDialog)
