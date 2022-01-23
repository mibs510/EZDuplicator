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

import EZDuplicator.lib.EZDuplicator

gi_require_version('Gtk', '3.0')
from gi.repository import Gtk


class ConfirmAppRestarDialog(Gtk.Dialog):
    """ Main window with all components. """

    def __init__(self, pids, parent):
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
                    'ConfirmAppRestarDialog',
                    'ConfirmAppRestarDialog_Cancel',
                    'ConfirmAppRestarDialog_Confirm',
                ]
            )
        except Exception as ex:
            logging.exception(ex)
            sys.exit(1)

        # Get gui objects
        self.ConfirmAppRestarDialog = self.builder.get_object('ConfirmAppRestarDialog')
        self.ConfirmAppRestarDialog_Cancel = self.builder.get_object('ConfirmAppRestarDialog_Cancel')
        self.ConfirmAppRestarDialog_Confirm = self.builder.get_object('ConfirmAppRestarDialog_Confirm')
        self.builder.connect_signals(self)
        self.pids = pids

        self.ConfirmAppRestarDialog.show_all()
        self.ConfirmAppRestarDialog.set_transient_for(parent)

    def on_ConfirmAppRestarDialog_Cancel_clicked(self, widget, user_data=None):
        """ Handler for ConfirmAppRestarDialog_Cancel.clicked. """
        self.ConfirmAppRestarDialog.destroy()

    def on_ConfirmAppRestarDialog_Confirm_clicked(self, widget, user_data=None):
        """ Handler for ConfirmAppRestarDialog_Confirm.clicked. """
        logging.info("Restarting EZ Duplicator app...")
        argv = ""
        for pid in self.pids:
            pid = str(pid)
            if pid != str(self.pids[-1]):
                argv += pid + " "
            else:
                argv += pid
        command = "python3.9 {}/restart_app.py {}".format(EZDuplicator.lib.EZDuplicator.__root_dir__, argv)
        os.system(command)
