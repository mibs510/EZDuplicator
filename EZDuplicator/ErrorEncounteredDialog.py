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


class ErrorEncounteredDialog(Gtk.Dialog):
    """ Main window with all components. """

    def __init__(self, msg, qrcode_filename):
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
                    'ErrorEncounteredDialog',
                    'ErrorEncounteredDialog_MessageLabel',
                    'ErrorEncounteredDialog_Ok',
                    'ErrorEncounteredDialog_QRCodeImage',
                    'ErrorEncounteredDialog_TitleLabel',
                ]
            )
        except Exception as ex:
            logging.exception(ex)
            sys.exit(1)

        # Get gui objects
        self.ErrorEncounteredDialog = self.builder.get_object('ErrorEncounteredDialog')
        self.ErrorEncounteredDialog_MessageLabel = self.builder.get_object('ErrorEncounteredDialog_MessageLabel')
        self.ErrorEncounteredDialog_Ok = self.builder.get_object('ErrorEncounteredDialog_Ok')
        self.ErrorEncounteredDialog_QRCodeImage = self.builder.get_object('ErrorEncounteredDialog_QRCodeImage')
        self.ErrorEncounteredDialog_TitleLabel = self.builder.get_object('ErrorEncounteredDialog_TitleLabel')
        self.ErrorEncounteredDialog.show_all()
        self.builder.connect_signals(self)
        if len(msg) > 0:
            self.ErrorEncounteredDialog_MessageLabel.set_text(str(msg))
            if os.path.isfile(qrcode_filename):
                self.ErrorEncounteredDialog_QRCodeImage.set_from_file(qrcode_filename)
            else:
                logging.debug("{} was not found?".format(qrcode_filename))
        else:
            self.ErrorEncounteredDialog.destroy()

    def on_ErrorEncounteredDialog_Ok_clicked(self, widget, user_data=None):
        """ Handler for ErrorEncounteredDialog_Ok.clicked. """
        self.ErrorEncounteredDialog.destroy()
