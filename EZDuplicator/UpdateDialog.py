"""

Copyright (c) 2021 Connor McMillan <connor@mcmillan.website>. All rights reserved.

This work is licensed under the terms of the MIT license.
For a copy, see <https://opensource.org/licenses/MIT>.

"""

import logging
import multiprocessing
import os
import sys
from multiprocessing import Process
from pathlib import Path

from gi import require_version as gi_require_version

import EZDuplicator.WTHDialog
import EZDuplicator.lib.EZDuplicator
import EZDuplicator.lib.Updates
import EZDuplicator.version

gi_require_version('Gtk', '3.0')
from gi.repository import Gtk, GLib


class UpdateDialog(Gtk.Dialog):
    """ Main window with all components. """

    def __init__(self, pids, parent):
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
                    'UpdateDialog',
                    'UpdateDialog_CancelButton',
                    'UpdateDialog_CancelLabel',
                    'UpdateDialog_CancelSpinner',
                    'UpdateDialog_Image',
                    'UpdateDialog_Label',
                    'UpdateDialog_UpdateButton',
                    'UpdateDialog_UpdateLabel',
                    'UpdateDialog_UpdateSpinner',
                ]
            )
        except Exception as ex:
            logging.exception(ex)
            sys.exit(1)

        # Get gui objects
        self.UpdateDialog = self.builder.get_object('UpdateDialog')
        self.UpdateDialog_CancelButton = self.builder.get_object('UpdateDialog_CancelButton')
        self.UpdateDialog_CancelLabel = self.builder.get_object('UpdateDialog_CancelLabel')
        self.UpdateDialog_CancelSpinner = self.builder.get_object('UpdateDialog_CancelSpinner')
        self.UpdateDialog_Image = self.builder.get_object('UpdateDialog_Image')
        self.UpdateDialog_Label = self.builder.get_object('UpdateDialog_Label')
        self.UpdateDialog_UpdateButton = self.builder.get_object('UpdateDialog_UpdateButton')
        self.UpdateDialog_UpdateLabel = self.builder.get_object('UpdateDialog_UpdateLabel')
        self.UpdateDialog_UpdateSpinner = self.builder.get_object('UpdateDialog_UpdateSpinner')
        self.builder.connect_signals(self)
        self.UpdateDialog.show_all()
        self.UpdateDialog.set_transient_for(parent)
        self.pids = pids
        self.manager = multiprocessing.Manager()
        self.exception = self.manager.Value(str, "")
        self.update_status = self.manager.Value(str, "")
        self.restart = False

        self.UpdateDialog_UpdateButton.set_sensitive(False)
        self.UpdateDialog_Label.set_text("Checking...")
        self.secrets = EZDuplicator.lib.EZDuplicator.Secrets()

        if self.secrets.oos:
            EZDuplicator.WTHDialog.WTHDialog(self.secrets.ex_msg)
            self.UpdateDialog.destroy()

        """ Check for update process """
        self.check_for_update_parent, self.check_for_update_child = multiprocessing.Pipe(duplex=False)
        self.check_for_update_proc = Process(target=EZDuplicator.lib.Updates.check_for_update_process,
                                             args=(self.check_for_update_child, self.exception, self.update_status,
                                                   self.secrets,),
                                             daemon=False)
        """ Do not close the child handle as cancel() will not be able to communicate with cancel_io_wait() """
        # self.check_for_update_child.close()
        GLib.io_add_watch(self.check_for_update_parent.fileno(), GLib.IO_IN, self.check_for_update_io_watch)

        """ Update Process """
        self.update_parent, self.update_child = multiprocessing.Pipe(duplex=False)
        self.update_proc = Process(target=EZDuplicator.lib.Updates.update_process,
                                   args=(self.update_child, self.exception, self.secrets,), daemon=False)
        self.check_for_update_proc.start()
        """ Do not close the child handle as cancel() will not be able to communicate with cancel_io_wait() """
        # self.update_child.close()
        GLib.io_add_watch(self.update_parent.fileno(), GLib.IO_IN, self.update_io_watch)

    def on_UpdateDialog_CancelButton_clicked(self, widget, user_data=None):
        """ Handler for UpdateDialog_CancelButton.clicked. """
        if self.restart:
            self.clean_up()
            self.restart_app()
        else:
            self.clean_up()
            self.UpdateDialog.destroy()

    def on_UpdateDialog_UpdateButton_clicked(self, widget, user_data=None):
        """ Handler for UpdateDialog_UpdateButton.clicked. """
        self.update_proc.start()

    def check_for_update_io_watch(self, source, condition):
        assert self.check_for_update_parent.poll()
        try:
            msg = self.check_for_update_parent.recv()
        except EOFError:
            return False

        if "update_status.True" in msg:
            self.UpdateDialog_Label.set_text(self.update_status.get())
            self.UpdateDialog_UpdateButton.set_sensitive(True)
            return True

        if "update_status.None" in msg:
            self.UpdateDialog_Image.set_from_file(
                str(Path(__file__).parent.absolute()) + "/res/updated-128.png")
            self.UpdateDialog_Label.set_text(
                "EZ Duplicator is up-to-date!\nVersion {}".format(EZDuplicator.version.__version__))
            self.UpdateDialog_UpdateButton.set_sensitive(False)
            self.UpdateDialog_CancelLabel.set_label("Close")
            return True

        if "check_for_update_process().Exception" in msg:
            """ Terminate main sub-process check_for_update_process() """
            EZDuplicator.WTHDialog.WTHDialog(self.exception.get())
            self.kill_check_update_process()
            self.manager.shutdown()
            del self.manager
            self.UpdateDialog.destroy()
            return True

        if "Finished" in msg:
            self.kill_check_update_process()

    def update_io_watch(self, source, condition):
        assert self.update_parent.poll()
        try:
            msg = self.update_parent.recv()
        except EOFError:
            return False

        if "self.UpdateDialog_UpdateSpinner.start()" in msg:
            """ Disable Cancel button """
            self.restart = True
            self.UpdateDialog_UpdateSpinner.start()
            self.UpdateDialog_CancelButton.set_sensitive(False)
            self.UpdateDialog_UpdateButton.set_sensitive(False)
            self.UpdateDialog_Label.set_text("Updating...")
            return True

        if "update_process().Exception" in msg:
            """ Terminate main sub-process update_process() """
            EZDuplicator.WTHDialog.WTHDialog(self.exception.get())
            self.UpdateDialog_UpdateButton.set_sensitive(True)
            self.UpdateDialog_UpdateSpinner.stop()
            self.reset_update_process()
            return True

        if "Finished" in msg:
            self.UpdateDialog_UpdateSpinner.stop()
            self.UpdateDialog_CancelButton.set_sensitive(True)
            self.UpdateDialog_CancelLabel.set_label("Restart")
            self.UpdateDialog_Image.set_from_file(
                str(Path(__file__).parent.absolute()) + "/res/updated-128.png")
            self.UpdateDialog_Label.set_text(
                "EZ Duplicator successfully updated!\nVersion: {}\nA restart is required.".format(
                    EZDuplicator.version.__version__))
            self.kill_update_process()
        return True

    def reset_update_process(self):
        self.kill_update_process()
        self.exception.set("")
        self.update_status.set("")
        self.update_proc = Process(target=EZDuplicator.lib.Updates.update_process,
                                   args=(self.update_child, self.exception,), daemon=False)

    def kill_check_update_process(self):
        while self.check_for_update_proc.is_alive():
            self.check_for_update_proc.terminate()
        self.check_for_update_proc.close()

    def kill_update_process(self):
        while self.update_proc.is_alive():
            self.update_proc.terminate()
        self.update_proc.close()

    def clean_up(self):
        self.manager.shutdown()
        del self.manager

    def restart_app(self):
        self.UpdateDialog.destroy()

        logging.info("Restarting EZ Duplicator app...")
        argv = ""
        for pid in self.pids:
            pid = str(pid)
            if pid != str(self.pids[-1]):
                argv += pid + " "
            else:
                argv += pid
        command = "python3.9 {}/restart_app.py {}".format(EZDuplicator.lib.EZDuplicator.__root_dir__, argv)
        os.system(command)
