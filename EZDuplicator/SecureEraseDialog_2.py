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
from gi.overrides.GdkPixbuf import GdkPixbuf
from gi.repository import Gtk, GLib

import EZDuplicator.QADialog
import EZDuplicator.lib.SecureErase
import EZDuplicator.lib.EZDuplicator

gi_require_version('Gtk', '3.0')


class SecureEraseDialog_2(Gtk.Dialog):
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
                    'SecureEraseDialog_2',
                    'SecureEraseDialog_2_CancelButton',
                    'SecureEraseDialog_2_CancelSpinner',
                    'SecureEraseDialog_2_FinishButton',
                    'SecureEraseDialog_2_Image',
                    'SecureEraseDialog_2_Label',
                    'SecureEraseDialog_2_ProgressBar',
                    'SecureEraseDialog_2_QAButton',
                ]
            )
        except Exception as ex:
            logging.error(ex)
            sys.exit(1)

        # Get gui objects
        self.SecureEraseDialog_2 = self.builder.get_object('SecureEraseDialog_2')
        self.SecureEraseDialog_2_CancelButton = self.builder.get_object('SecureEraseDialog_2_CancelButton')
        self.SecureEraseDialog_2_CancelSpinner = self.builder.get_object('SecureEraseDialog_2_CancelSpinner')
        self.SecureEraseDialog_2_FinishButton = self.builder.get_object('SecureEraseDialog_2_FinishButton')
        self.SecureEraseDialog_2_Image = self.builder.get_object('SecureEraseDialog_2_Image')
        self.SecureEraseDialog_2_Image.set_from_animation(
            GdkPixbuf.PixbufAnimation.new_from_file(str(Path(__file__).parent.absolute()) + "/res/eraser-128.gif"))
        self.SecureEraseDialog_2_ProgressBar = self.builder.get_object('SecureEraseDialog_2_ProgressBar')
        self.SecureEraseDialog_2_Label = self.builder.get_object('SecureEraseDialog_2_Label')
        self.SecureEraseDialog_2_QAButton = self.builder.get_object('SecureEraseDialog_2_QAButton')
        self.SecureEraseDialog_2.show_all()
        self.builder.connect_signals(self)

        """ Disable the finish & QA results button until we actually finish erasing drives. """
        self.SecureEraseDialog_2_FinishButton.set_sensitive(False)
        self.SecureEraseDialog_2_QAButton.set_sensitive(False)

        """ Begin erasing drives """
        self.source_bypath = EZDuplicator.lib.EZDuplicator.get_config_setting('source_dev_path')
        self.number_of_usbs = EZDuplicator.lib.EZDuplicator.get_number_or_list_of_usbs('number', self.source_bypath)
        self.number_of_tasks = (self.number_of_usbs * 3) + 3
        self.number_of_completed_tasks = 0
        self.manager = multiprocessing.Manager()
        self.failed_drives = self.manager.list()
        self.pids = self.manager.list()

        """ Cancel Process """
        self.cancel_parent, self.cancel_child = multiprocessing.Pipe(duplex=False)
        self.cancel_proc = Process(target=EZDuplicator.lib.SecureErase.cancel,
                                   args=(self.number_of_usbs, self.pids, self.cancel_child), daemon=False)
        """ Do not close the child handle as update_io_watch() will not be able to communicate with cancel_io_wait() """
        # self.update_child.close()
        GLib.io_add_watch(self.cancel_parent.fileno(), GLib.IO_IN, self.cancel_io_watch)

        """ Stop Process """
        self.stop_parent, self.stop_child = multiprocessing.Pipe(duplex=False)
        self.stop_proc = Process(target=EZDuplicator.lib.SecureErase.stop,
                                 args=(self.pids, self.stop_child), daemon=False)
        """ Do not close the child handle as stop() will not be able to communicate with stop_io_wait() """
        # self.upload_child.close()
        GLib.io_add_watch(self.stop_parent.fileno(), GLib.IO_IN, self.stop_io_watch)

        """ Main Process """
        self.secure_erase_parent, self.secure_erase_child = multiprocessing.Pipe(duplex=False)
        self.secure_erase_proc = Process(target=EZDuplicator.lib.SecureErase.secure_erase_process,
                                         args=(self.secure_erase_child, self.pids, self.failed_drives), daemon=False)
        self.secure_erase_proc.start()
        self.secure_erase_child.close()
        GLib.io_add_watch(self.secure_erase_parent.fileno(), GLib.IO_IN, self.secure_erase_process_io_watch)

    def secure_erase_process_io_watch(self, source, condition):
        assert self.secure_erase_parent.poll()
        try:
            msg = self.secure_erase_parent.recv()
        except EOFError:
            return False

        if "Bump" in msg:
            self.number_of_completed_tasks = self.number_of_completed_tasks + 1
            progress = (self.number_of_completed_tasks / self.number_of_tasks)
            """ Bounce it back down to the maximum 100% if needed """
            if progress > 1:
                logging.info("progress = {}, so reassigning to 1".format(progress))
                progress = 1
            self.SecureEraseDialog_2_ProgressBar.set_fraction(progress)
            self.SecureEraseDialog_2_ProgressBar.set_text("{0:.0%}".format(progress))
            return True

        if "Cleanup" in msg:
            self.SecureEraseDialog_2_ProgressBar.set_fraction(.99)
            self.SecureEraseDialog_2_ProgressBar.set_text("{0:.0%}".format(.99))

        if "Enable_QADialog_Button" in msg:
            self.SecureEraseDialog_2_QAButton.set_sensitive(True)
            return True

        if "Stop" in msg:
            self.stop_proc.start()
            self.SecureEraseDialog_2_Image.set_from_file(
                str(Path(__file__).parent.absolute()) + "/res/red-warning-128.png")
            self.BPBDuplicationDialog_Label.set_text("Fatal Error: Review debug console for further details.")
            return True

        self.number_of_completed_tasks = self.number_of_completed_tasks + 1

        """ Just incase if the progres bar doesn't quite fully reach 100% """
        if "Finished" in msg:
            self.SecureEraseDialog_2_ProgressBar.set_fraction(1)
            self.SecureEraseDialog_2_ProgressBar.set_text("{0:.0%}".format(1))
            ''' When the progress bar reaches 100%, disable the Cancel button and enable the Finish button.'''
            if len(self.failed_drives) > 0:
                self.SecureEraseDialog_2_Label.set_text("Secure erase completed with some issues!\n"
                                                        "Review QA Report for further details.")
                self.SecureEraseDialog_2_Image.set_from_file(
                    str(Path(__file__).parent.absolute()) + "/res/caution-sign-128.png")
            else:
                self.SecureEraseDialog_2_Label.set_text("Secure erase completed successfully!")
                self.SecureEraseDialog_2_Image.set_from_file(
                    str(Path(__file__).parent.absolute()) + "/res/check-128.png")

            self.SecureEraseDialog_2_FinishButton.set_sensitive(True)
            self.SecureEraseDialog_2_CancelButton.set_sensitive(False)
            return True

        return True

    def cancel_io_watch(self, source, condition):
        assert self.cancel_parent.poll()
        try:
            msg = self.cancel_parent.recv()
        except EOFError:
            return False

        if "spinner" in msg:
            """ Disable Cancel button since we need time to stop everyone """
            self.SecureEraseDialog_2_CancelSpinner.start()
            self.SecureEraseDialog_2_CancelButton.set_sensitive(False)
            self.SecureEraseDialog_2_Label.set_text("Cancelling...")
            return True
        if "terminate" in msg:
            """ Terminate main sub-process secure_erase_process() """
            while self.secure_erase_proc.is_alive():
                self.secure_erase_proc.terminate()
            self.secure_erase_proc.close()
            return True
        if "destroy" in msg:
            self.manager.shutdown()
            del self.manager
            while self.cancel_proc.is_alive():
                self.cancel_proc.terminate()
            self.cancel_proc.close()
            self.SecureEraseDialog_2.destroy()
        return True

    def stop_io_watch(self, source, condition):
        assert self.stop_parent.poll()
        try:
            msg = self.stop_parent.recv()
        except EOFError:
            return False

        if "spinner" in msg:
            """ Disable Cancel button since we need time to stop everyone """
            self.SecureEraseDialog_2_CancelSpinner.start()
            self.SecureEraseDialog_2_CancelButton.set_sensitive(False)
            return True
        if "terminate" in msg:
            """ Terminate main sub-process secure_erase_process() """
            while self.secure_erase_proc.is_alive():
                self.secure_erase_proc.terminate()
            self.secure_erase_proc.close()
            return True
        if "stop" in msg:
            self.manager.shutdown()
            del self.manager
            while self.stop_proc.is_alive():
                self.stop_proc.terminate()
            self.stop_parent.close()
            self.SecureEraseDialog_2_CancelSpinner.stop()
            self.SecureEraseDialog_2_FinishButton.set_label("Close")
            self.SecureEraseDialog_2_FinishButton.set_sensitive(True)
            return True
        return True

    def on_SecureEraseDialog_2_CancelButton_clicked(self, widget, user_data=None):
        """ Handler for SecureEraseDialog_2_CancelButton.clicked. """
        self.cancel_proc.start()

    def on_SecureEraseDialog_2_FinishButton_clicked(self, widget, user_data=None):
        """ Handler for SecureEraseDialog_2_FinishButton.clicked. """
        self.manager.shutdown()
        del self.manager
        while self.secure_erase_proc.is_alive():
            self.secure_erase_proc.terminate()
        self.secure_erase_proc.close()
        self.SecureEraseDialog_2.destroy()

    def on_SecureEraseDialog_2_QAButton_clicked(self, widget, user_data=None):
        """ Handler for SecureEraseDialog_2_QAButton.clicked. """
        EZDuplicator.QADialog.QADialog("Secure Erase QA Results",
                                       "The following drives failed to securely\nerase during one or more passes.",
                                       self.failed_drives)
