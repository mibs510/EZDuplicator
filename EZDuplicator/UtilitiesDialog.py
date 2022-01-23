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


class UtilitiesDialog(Gtk.Dialog):
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
                    'UtilitiesDialog',
                    'UtilitiesDialog_CloseButton',
                    'UtilitiesDialog_FileManagerButton',
                    'UtilitiesDialog_TaskManagerButton',
                    'UtilitiesDialog_TerminalButton',
                    'UtilitiesDialog_TextEditorButton',
                    'UtilitiesDialog_WebBrowserButton',
                ]
            )
        except Exception as ex:
            logging.exception(ex)
            sys.exit(1)

        # Get gui objects
        self.UtilitiesDialog = self.builder.get_object('UtilitiesDialog')
        self.UtilitiesDialog_CloseButton = self.builder.get_object('UtilitiesDialog_CloseButton')
        self.UtilitiesDialog_FileManagerButton = self.builder.get_object('UtilitiesDialog_FileManagerButton')
        self.UtilitiesDialog_TaskManagerButton = self.builder.get_object('UtilitiesDialog_TaskManagerButton')
        self.UtilitiesDialog_TerminalButton = self.builder.get_object('UtilitiesDialog_TerminalButton')
        self.UtilitiesDialog_TextEditorButton = self.builder.get_object('UtilitiesDialog_TextEditorButton')
        self.UtilitiesDialog_WebBrowserButton = self.builder.get_object('UtilitiesDialog_WebBrowserButton')

        self.builder.connect_signals(self)
        self.UtilitiesDialog.show_all()

    def on_UtilitiesDialog_CloseButton_clicked(self, widget, user_data=None):
        """ Handler for UtilitiesDialog_CloseButton.clicked. """
        self.UtilitiesDialog.destroy()

    def on_UtilitiesDialog_FileManagerButton_clicked(self, widget, user_data=None):
        """ Handler for UtilitiesDialog_FileManagerButton.clicked. """
        os.system("nautilus &>/dev/null")

    def on_UtilitiesDialog_TaskManagerButton_clicked(self, widget, user_data=None):
        """ Handler for UtilitiesDialog_TaskManagerButton.clicked. """
        os.system("gnome-system-monitor &>/dev/null")

    def on_UtilitiesDialog_TerminalButton_clicked(self, widget, user_data=None):
        """ Handler for UtilitiesDialog_TerminalButton.clicked. """
        os.system("gnome-terminal")

    def on_UtilitiesDialog_TextEditorButton_clicked(self, widget, user_data=None):
        """ Handler for UtilitiesDialog_TextEditorButton.clicked. """
        os.system("gedit &>/dev/null")

    def on_UtilitiesDialog_WebBrowserButton_clicked(self, widget, user_data=None):
        """ Handler for UtilitiesDialog_WebBrowserButton.clicked. """
        os.system("export DISPLAY=\":0\" && firefox &>/dev/null")
