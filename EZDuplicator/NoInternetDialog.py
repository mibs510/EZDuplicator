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


class NoInternetDialog(Gtk.Dialog):
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
                    'NoInternetDialog',
                    'NoInternetDialog_Ok',
                ]
            )
        except Exception as ex:
            logging.exception(ex)
            sys.exit(1)

        # Get gui objects
        self.NoInternetDialog = self.builder.get_object('NoInternetDialog')
        self.NoInternetDialog_Ok = self.builder.get_object('NoInternetDialog_Ok')
        self.NoInternetDialog.show_all()
        self.NoInternetDialog.set_transient_for(parent)
        self.builder.connect_signals(self)

    def on_NoInternetDialog_Ok_clicked(self, widget, user_data=None):
        """ Handler for NoInternetDialog_Ok.clicked. """
        self.NoInternetDialog.destroy()
