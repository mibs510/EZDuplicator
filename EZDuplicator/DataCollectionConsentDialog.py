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


class DataCollectionConsentDialog(Gtk.Dialog):
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
                    'DataCollectionConsentDialog',
                    'DataCollectionConsentDialog_Accept',
                    'DataCollectionConsentDialog_Close',
                    'DataCollectionConsentDialog_Decline',
                ]
            )
        except Exception as ex:
            logging.exception(ex)
            sys.exit(1)

        # Get gui objects
        self.DataCollectionConsentDialog = self.builder.get_object('DataCollectionConsentDialog')
        self.DataCollectionConsentDialog_Accept = self.builder.get_object('DataCollectionConsentDialog_Accept')
        self.DataCollectionConsentDialog_Close = self.builder.get_object('DataCollectionConsentDialog_Close')
        self.DataCollectionConsentDialog_Decline = self.builder.get_object('DataCollectionConsentDialog_Decline')
        self.builder.connect_signals(self)

        if EZDuplicator.lib.EZDuplicator.get_config_setting("improve_software") == "":
            self.DataCollectionConsentDialog.show_all()
        else:
            EZDuplicator.lib.EZDuplicator.improve_software()
            self.DataCollectionConsentDialog.destroy()


    def on_DataCollectionConsentDialog_Accept_clicked(self, widget, user_data=None):
        """ Handler for DataCollectionConsentDialog_Accept.clicked. """
        try:
            EZDuplicator.lib.EZDuplicator.set_config_setting("improve_software", "True")
            EZDuplicator.lib.EZDuplicator.improve_software()
            self.DataCollectionConsentDialog.destroy()
        except Exception as ex:
            logging.exception(ex)

    def on_DataCollectionConsentDialog_Close_clicked(self, widget, user_data=None):
        """ Handler for DataCollectionConsentDialog_Close.clicked. """
        self.DataCollectionConsentDialog.destroy()

    def on_DataCollectionConsentDialog_Decline_clicked(self, widget, user_data=None):
        """ Handler for DataCollectionConsentDialog_Decline.clicked. """
        try:
            EZDuplicator.lib.EZDuplicator.set_config_setting("improve_software", "False")
            EZDuplicator.lib.EZDuplicator.improve_software()
            self.DataCollectionConsentDialog.destroy()
        except Exception as ex:
            logging.exception(ex)
