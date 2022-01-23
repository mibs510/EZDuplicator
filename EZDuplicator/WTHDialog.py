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


class WTHDialog(Gtk.Dialog):
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
                    'WTHDialog',
                    'WTHDialog_Ok',
                    'WTH_Msg_Label',
                ]
            )
        except Exception as ex:
            logging.error(ex)
            sys.exit(1)

        # Get gui objects
        self.WTHDialog = self.builder.get_object('WTHDialog')
        self.WTHDialog_Ok = self.builder.get_object('WTHDialog_Ok')
        self.WTH_Msg_Label = self.builder.get_object('WTH_Msg_Label')

        self.WTHDialog.show_all()
        self.builder.connect_signals(self)

        self.WTH_Msg_Label.set_text(str(msg))

    def on_WTHDialog_Ok_clicked(self, widget, user_data=None):
        """ Handler for WTHDialog_Ok.clicked. """
        self.WTHDialog.destroy()
