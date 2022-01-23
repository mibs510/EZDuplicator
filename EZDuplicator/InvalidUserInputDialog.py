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


class InvalidUserInputDialog(Gtk.Dialog):
    """ Main window with all components. """

    def __init__(self, msg):
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
                    'InvalidUserInputDialog',
                    'InvalidUserInputDialog_Label',
                    'InvalidUserInputDialog_Ok',
                ]
            )
        except Exception as ex:
            logging.exception(ex)
            sys.exit(1)

        # Get gui objects
        self.InvalidUserInputDialog = self.builder.get_object('InvalidUserInputDialog')
        self.InvalidUserInputDialog_Label = self.builder.get_object('InvalidUserInputDialog_Label')
        self.InvalidUserInputDialog_Ok = self.builder.get_object('InvalidUserInputDialog_Ok')
        self.InvalidUserInputDialog_Label.set_text(str(msg))
        self.InvalidUserInputDialog.show_all()
        self.builder.connect_signals(self)

    def on_InvalidUserInputDialog_Ok_clicked(self, widget, user_data=None):
        """ Handler for InvalidUserInputDialog_Ok.clicked. """
        self.InvalidUserInputDialog.destroy()
