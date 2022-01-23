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

import EZDuplicator.PowerOnHubDialog

gi_require_version('Gtk', '3.0')

from gi.repository import Gtk


class SecureEraseDialog_1(Gtk.Dialog):
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
                    'SecureEraseDialog_1',
                    'SecureEraseDialog_1_CancelButton',
                    'SecureEraseDialog_1_ContinueButton',
                ]
            )
        except Exception as ex:
            logging.error(ex)
            sys.exit(1)

        # Get gui objects
        self.SecureEraseDialog_1 = self.builder.get_object('SecureEraseDialog_1')
        self.SecureEraseDialog_1_CancelButton = self.builder.get_object('SecureEraseDialog_1_CancelButton')
        self.SecureEraseDialog_1_ContinueButton = self.builder.get_object('SecureEraseDialog_1_ContinueButton')
        self.SecureEraseDialog_1.show_all()
        self.builder.connect_signals(self)
        self.option = option

    def on_SecureEraseDialog_1_CancelButton_clicked(self, widget, user_data=None):
        """ Handler for SecureEraseDialog_1_CancelButton.clicked. """
        self.SecureEraseDialog_1.destroy()

    def on_SecureEraseDialog_1_ContinueButton_clicked(self, widget, user_data=None):
        """ Handler for SecureEraseDialog_1_ContinueButton.clicked. """
        EZDuplicator.PowerOnHubDialog.PowerOnHubDialog(self.option)
        self.SecureEraseDialog_1.destroy()

