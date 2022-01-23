"""

Copyright (c) 2021 Connor McMillan <connor@mcmillan.website>. All rights reserved.

This work is licensed under the terms of the MIT license.
For a copy, see <https://opensource.org/licenses/MIT>.

"""
import json
import logging
import os
import sys
from pathlib import Path

from gi import require_version as gi_require_version

import EZDuplicator.ConsentDialog
import EZDuplicator.NoInternetDialog
import EZDuplicator.WTHDialog
import EZDuplicator.lib.EZDuplicator

gi_require_version('Gtk', '3.0')

from gi.repository import Gtk


class DebugDialog(Gtk.Dialog):
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
                    'Close',
                    'DebugDialog',
                    'SendLog',
                    'Type',
                    'grid',
                    'scrollable_treelist',
                ]
            )
        except Exception as ex:
            logging.exception(ex)
            sys.exit(1)

        # Get gui objects
        self.Close = self.builder.get_object('Close')
        self.DebugDialog = self.builder.get_object('DebugDialog')
        self.SendLog = self.builder.get_object('SendLog')
        self.Type = self.builder.get_object('Type')
        self.grid = self.builder.get_object('grid')
        self.scrollable_treelist = self.builder.get_object('scrollable_treelist')
        wth_message = ""

        # Creating the ListStore model
        self.debug_entries_liststore = Gtk.ListStore(str, str, str, str)
        if not os.path.isfile(EZDuplicator.lib.EZDuplicator.__json_log_file__):
            wth_message = "Log file does not exist. No logs to read from."
            self.Type.set_sensitive(False)
            self.SendLog.set_sensitive(False)
        else:
            with open(EZDuplicator.lib.EZDuplicator.__json_log_file__, "r") as file:
                for line in reversed(list(file)):
                    try:
                        dic = json.loads(line)
                        row = []
                        row.append(dic['asctime'])
                        row.append(dic['levelname'])
                        row.append(dic['filename'] + ":" + dic['funcName'] + "():" + str(dic['lineno']))
                        row.append(dic['message'])
                        self.debug_entries_liststore.append(list(row))
                    except Exception as ex:
                        """logging.exception(ex, exc_info=False)"""
                        logging.exception(ex)

        self.current_debug_entry_filter = None

        # Creating the filter, feeding it with the liststore model
        self.type_filter = self.debug_entries_liststore.filter_new()
        # setting the filter function, note that we're not using the
        self.type_filter.set_visible_func(self.type_filter_func)

        # creating the treeview, making it use the filter as a model, and adding the columns
        self.treeview = Gtk.TreeView(model=self.type_filter)
        for i, column_title in enumerate(
                ["Date & Time", "Type", "Function/Method", "Message"]
        ):
            renderer = Gtk.CellRendererText()
            column = Gtk.TreeViewColumn(column_title, renderer, text=i)
            self.treeview.append_column(column)
        self.scrollable_treelist.set_vexpand(True)
        # self.grid.attach(self.scrollable_treelist, 0, 0, 8, 10)
        self.scrollable_treelist.add(self.treeview)
        self.DebugDialog.show_all()
        self.DebugDialog.set_transient_for(parent)
        self.builder.connect_signals(self)

        if len(wth_message) > 0:
            EZDuplicator.WTHDialog.WTHDialog(wth_message)

    def on_Close_clicked(self, widget, user_data=None):
        """ Handler for Close.clicked. """
        self.DebugDialog.destroy()

    def on_SendLog_clicked(self, widget, user_data=None):
        """ Handler for SendLog.clicked. """
        if EZDuplicator.lib.EZDuplicator.has_internet_connection():
            logging.debug("Detected a valid internet connection")
            EZDuplicator.ConsentDialog.ConsentDialog()
        else:
            logging.debug("Failed to detect a valid internet connection")
            EZDuplicator.NoInternetDialog.NoInternetDialog(self.DebugDialog)

    def on_Type_changed(self, widget, user_data=None):
        """ Handler for Type.changed. """
        # we set the current language filter to the button's label
        self.current_debug_entry_filter = widget.get_active_text()
        # we update the filter, which updates in turn the view
        self.type_filter.refilter()

    def type_filter_func(self, model, iter, data):
        """Tests if the language in the row is the one in the filter"""
        if (
                self.current_debug_entry_filter is None
                or self.current_debug_entry_filter == "All"
        ):
            return True
        else:
            return model[iter][1] == self.current_debug_entry_filter
