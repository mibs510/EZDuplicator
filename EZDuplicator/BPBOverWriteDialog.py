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

import EZDuplicator.ConnectSourceMediaDialog

gi_require_version('Gtk', '3.0')

from gi.repository import Gtk


class BPBOverWriteDialog(Gtk.Dialog):
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
                    'BPBOverWriteDialog',
                    'BPBOverWriteDialog_CancelButton',
                    'BPBOverWriteDialog_ContinueButton',
                ]
            )
        except Exception as ex:
            logging.error(ex)
            sys.exit(1)

        # Get gui objects
        self.BPBOverWriteDialog = self.builder.get_object('BPBOverWriteDialog')
        self.BPBOverWriteDialog_CancelButton = self.builder.get_object('BPBOverWriteDialog_CancelButton')
        self.BPBOverWriteDialog_ContinueButton = self.builder.get_object('BPBOverWriteDialog_ContinueButton')

        self.BPBOverWriteDialog.show_all()
        self.builder.connect_signals(self)

    def on_OverWriteDialog_CancelButton_clicked(self, widget, user_data=None):
        """ Handler for BPBOverWriteDialog_CancelButton.clicked. """
        self.BPBOverWriteDialog.destroy()

    def on_OverWriteDialog_ContinueButton_clicked(self, widget, user_data=None):
        """ Handler for BPBOverWriteDialog_ContinueButton.clicked. """
        EZDuplicator.ConnectSourceMediaDialog.ConnectSourceMediaDialog("BPBDuplication")
        self.BPBOverWriteDialog.destroy()
