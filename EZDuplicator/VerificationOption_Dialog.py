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


class VerificationOption_Dialog(Gtk.Dialog):
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
                    'BPBVerification_Button',
                    'DataOnlyVerification_Button',
                    'VerificationOption_CancelButton',
                    'VerificationOption_Dialog',
                ]
            )
        except Exception as ex:
            logging.error(ex)
            sys.exit(1)

        # Get gui objects
        self.BPBVerification_Button = self.builder.get_object('BPBVerification_Button')
        self.DataOnlyVerification_Button = self.builder.get_object('DataOnlyVerification_Button')
        self.VerificationOption_CancelButton = self.builder.get_object('VerificationOption_CancelButton')
        self.VerificationOption_Dialog = self.builder.get_object('VerificationOption_Dialog')
        self.builder.connect_signals(self)
        self.VerificationOption_Dialog.show_all()

    def on_BPBVerification_Button_clicked(self, widget, user_data=None):
        """ Handler for BPBVerification_Button.clicked. """
        EZDuplicator.ConnectSourceMediaDialog.ConnectSourceMediaDialog("BPBVerification")
        self.VerificationOption_Dialog.destroy()

    def on_DataOnlyVerification_Button_clicked(self, widget, user_data=None):
        """ Handler for DataOnlyVerification_Button.clicked. """
        EZDuplicator.ConnectSourceMediaDialog.ConnectSourceMediaDialog("DataOnlyVerification")
        self.VerificationOption_Dialog.destroy()

    def on_VerificationOption_CancelButton_clicked(self, widget, user_data=None):
        """ Handler for VerificationOption_CancelButton.clicked. """
        self.VerificationOption_Dialog.destroy()
