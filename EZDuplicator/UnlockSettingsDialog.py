"""

Copyright (c) 2021 Connor McMillan <connor@mcmillan.website>. All rights reserved.

This work is licensed under the terms of the MIT license.
For a copy, see <https://opensource.org/licenses/MIT>.

"""
import logging
import os
import subprocess
import sys
from pathlib import Path

from gi import require_version as gi_require_version

import EZDuplicator.lib.EZDuplicator

gi_require_version('Gtk', '3.0')

from gi.repository import Gtk


class UnlockSettingsDialog(Gtk.Dialog):
    """ Main window with all components. """

    def __init__(self, theirself, parent):
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
                    'Cancel',
                    'IncorrectPINInfoBar_Message',
                    'IncorrectPIN_InfoBar',
                    'PinCode_Entry',
                    'Unlock',
                    'UnlockSettingsDialog',
                ]
            )
        except Exception as ex:
            logging.exception(ex)
            sys.exit(1)

        # Get gui objects
        self.Cancel = self.builder.get_object('Cancel')
        self.IncorrectPINInfoBar_Message = self.builder.get_object('IncorrectPINInfoBar_Message')
        self.IncorrectPIN_InfoBar = self.builder.get_object('IncorrectPIN_InfoBar')
        self.PinCode_Entry = self.builder.get_object('PinCode_Entry')
        self.Unlock = self.builder.get_object('Unlock')
        self.UnlockSettingsDialog = self.builder.get_object('UnlockSettingsDialog')
        self.builder.connect_signals(self)
        self.UnlockSettingsDialog.show_all()
        self.SettingsDialog = theirself
        self.UnlockSettingsDialog.set_transient_for(parent)

        self.IncorrectPIN_InfoBar.hide()
        self.pin_code = EZDuplicator.lib.EZDuplicator.get_secret('unlock_settings_pin')

    def on_Cancel_clicked(self, widget, user_data=None):
        """ Handler for Cancel.clicked. """
        self.UnlockSettingsDialog.destroy()

    def on_PinCode_Entry_focus_in_event(self, widget, event, user_data=None):
        """ Handler for PinCode_Entry.focus-in-event. """
        subprocess.Popen("onboard")

    def on_PinCode_Entry_focus_out_event(self, widget, event, user_data=None):
        """ Handler for PinCode_Entry.focus-out-event. """
        subprocess.Popen(["pkill", "onboard"])

    def on_Unlock_clicked(self, widget, user_data=None):
        """ Handler for Unlock.clicked. """
        if self.PinCode_Entry.get_text() != self.pin_code:
            logging.warning("Incorrect PIN!")
            self.IncorrectPIN_InfoBar.show()
        else:
            self.SettingsDialog.SourceDevPath.set_sensitive(True)
            self.SettingsDialog.TwelveVCOMPort.set_sensitive(True)
            self.SettingsDialog.Repo.set_sensitive(True)
            self.SettingsDialog.UnlockButton.set_sensitive(False)
            self.SettingsDialog.DebugUtilities.set_sensitive(True)
            self.UnlockSettingsDialog.destroy()
