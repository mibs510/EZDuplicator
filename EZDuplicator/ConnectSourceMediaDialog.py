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
import EZDuplicator.lib.EZDuplicator

gi_require_version('Gtk', '3.0')

from gi.repository import Gtk


class ConnectSourceMediaDialog(Gtk.Dialog):
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
                    'ConnectSourceMediaDialog',
                    'ConnectSourceMediaDialog_CancelButton',
                    'ConnectSourceMediaDialog_ContinueButton',
                    'SourceMediaNotFoundInfoBar',
                ]
            )
        except Exception as ex:
            logging.error(ex)
            sys.exit(1)

        # Get gui objects
        self.ConnectSourceMediaDialog = self.builder.get_object('ConnectSourceMediaDialog')
        self.ConnectSourceMediaDialog_CancelButton = self.builder.get_object('ConnectSourceMediaDialog_CancelButton')
        self.ConnectSourceMediaDialog_ContinueButton = \
            self.builder.get_object('ConnectSourceMediaDialog_ContinueButton')
        self.SourceMediaNotFoundInfoBar = self.builder.get_object('SourceMediaNotFoundInfoBar')

        self.ConnectSourceMediaDialog.show_all()
        self.builder.connect_signals(self)

        self.option = option
        self.SourceMediaNotFoundInfoBar.hide()

    def on_ConnectSourceMediaDialog_CancelButton_clicked(self, widget, user_data=None):
        """ Handler for ConnectSourceMediaDialog_CancelButton.clicked. """
        self.ConnectSourceMediaDialog.destroy()

    def on_ConnectSourceMediaDialog_ContinueButton_clicked(self, widget, user_data=None):
        """ Handler for ConnectSourceMediaDialog_ContinueButton.clicked. """
        if EZDuplicator.lib.EZDuplicator.is_source_connected(
                EZDuplicator.lib.EZDuplicator.get_config_setting('source_dev_path')):
            EZDuplicator.PowerOnHubDialog.PowerOnHubDialog(self.option)
            self.ConnectSourceMediaDialog.destroy()
        else:
            self.SourceMediaNotFoundInfoBar.show()

    def on_SourceMediaNotFoundInfoBar_response(self, widget, response_id, user_data=None):
        """ Handler for SourceMediaNotFoundInfoBar.response. """
        pass
