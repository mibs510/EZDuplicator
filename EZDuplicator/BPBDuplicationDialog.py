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
import EZDuplicator.lib.BPBDuplication
import EZDuplicator.lib.EZDuplicator

gi_require_version('Gtk', '3.0')


class BPBDuplicationDialog(Gtk.Dialog):
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
                    'BPBDuplicationDialog',
                    'BPBDuplicationDialog_CancelButton',
                    'BPBDuplicationDialog_CancelSpinner',
                    'BPBDuplicationDialog_FinishButton',
                    'BPBDuplicationDialog_Image',
                    'BPBDuplicationDialog_Label',
                    'BPBDuplicationDialog_ProgressBar',
                    'BPBDuplicationDialog_QAButton',
                ]
            )
        except Exception as ex:
            logging.error(ex)
            sys.exit(1)

        # Get gui objects
        self.BPBDuplicationDialog = self.builder.get_object('BPBDuplicationDialog')
        self.BPBDuplicationDialog_CancelButton = self.builder.get_object('BPBDuplicationDialog_CancelButton')
        self.BPBDuplicationDialog_CancelSpinner = self.builder.get_object('BPBDuplicationDialog_CancelSpinner')
        self.BPBDuplicationDialog_FinishButton = self.builder.get_object('BPBDuplicationDialog_FinishButton')
        self.BPBDuplicationDialog_Image = self.builder.get_object('BPBDuplicationDialog_Image')
        self.BPBDuplicationDialog_Image.set_from_animation(
            GdkPixbuf.PixbufAnimation.new_from_file(
                str(Path(__file__).parent.absolute()) + "/res/binary-code-128.gif"))
        self.BPBDuplicationDialog_Label = self.builder.get_object('BPBDuplicationDialog_Label')
        self.BPBDuplicationDialog_ProgressBar = self.builder.get_object('BPBDuplicationDialog_ProgressBar')
        self.BPBDuplicationDialog_QAButton = self.builder.get_object('BPBDuplicationDialog_QAButton')

        self.BPBDuplicationDialog.show_all()
        self.builder.connect_signals(self)

        """ Disable the finish & QA results button until we actually finish duplicating drives. """
        self.BPBDuplicationDialog_FinishButton.set_sensitive(False)
        self.BPBDuplicationDialog_QAButton.set_sensitive(False)

        """ Begin BPB duplicating drives """
        """ 2 task per usb (one duplication & one qa) + 1 task to grab xxhsum hash from source drive"""
        self.source_bypath = EZDuplicator.lib.EZDuplicator.get_config_setting('source_dev_path')
        self.number_of_usbs = EZDuplicator.lib.EZDuplicator.get_number_or_list_of_usbs('number', self.source_bypath)
        self.number_of_tasks = (self.number_of_usbs * 2) + 3
        self.number_of_completed_tasks = 0
        self.manager = multiprocessing.Manager()
        self.failed_drives = self.manager.list()
        self.pids = self.manager.list()

        """ Cancel Process """
        self.cancel_parent, self.cancel_child = multiprocessing.Pipe(duplex=False)
        self.cancel_proc = Process(target=EZDuplicator.lib.BPBDuplication.cancel,
                                   args=(self.number_of_usbs, self.pids, self.cancel_child), daemon=False)
        """ Do not close the child handle as cancel() will not be able to communicate with cancel_io_wait() """
        # self.update_child.close()
        GLib.io_add_watch(self.cancel_parent.fileno(), GLib.IO_IN, self.cancel_io_watch)

        """ Stop Process """
        self.stop_parent, self.stop_child = multiprocessing.Pipe(duplex=False)
        self.stop_proc = Process(target=EZDuplicator.lib.BPBDuplication.stop,
                                 args=(self.pids, self.stop_child), daemon=False)
        """ Do not close the child handle as stop() will not be able to communicate with stop_io_wait() """
        # self.upload_child.close()
        GLib.io_add_watch(self.stop_parent.fileno(), GLib.IO_IN, self.stop_io_watch)

        """ Main Process """
        self.bpb_duplication_process_parent, self.bpb_duplication_process_child = multiprocessing.Pipe(duplex=False)
        self.bpb_duplication_proc = Process(target=EZDuplicator.lib.BPBDuplication.bpb_duplication_process,
                                            args=(self.bpb_duplication_process_child, self.pids, self.failed_drives),
                                            daemon=False)
        self.bpb_duplication_proc.start()
        self.bpb_duplication_process_child.close()
        GLib.io_add_watch(self.bpb_duplication_process_parent.fileno(), GLib.IO_IN, self.bpb_duplication_io_watch)

    def bpb_duplication_io_watch(self, source, condition):
        assert self.bpb_duplication_process_parent.poll()
        try:
            msg = self.bpb_duplication_process_parent.recv()
        except EOFError:
            return False

        if "Bump" in msg:
            self.number_of_completed_tasks = self.number_of_completed_tasks + 1
            progress = (self.number_of_completed_tasks / self.number_of_tasks)
            """ Bounce it back down to the maximum 100% if needed """
            if progress > 1:
                logging.info("progress = {}, so reassigning to 1".format(progress))
                progress = 1
            self.BPBDuplicationDialog_ProgressBar.set_fraction(progress)
            self.BPBDuplicationDialog_ProgressBar.set_text("{0:.0%}".format(progress))
            return True

        if "Cleanup" in msg:
            self.BPBDuplicationDialog_ProgressBar.set_fraction(.99)
            self.BPBDuplicationDialog_ProgressBar.set_text("{0:.0%}".format(.99))

        if "Enable_QADialog_Button" in msg:
            self.BPBDuplicationDialog_QAButton.set_sensitive(True)
            return True

        if "Stop" in msg:
            """ Initiate get_default_smtp_settings_io_watch() """
            self.stop_proc.start()
            self.BPBDuplicationDialog_Image.set_from_file(
                str(Path(__file__).parent.absolute()) + "/res/red-warning-128.png")
            self.BPBDuplicationDialog_Label.set_text("Fatal Error: Review debug console for further details.")
            return True

        self.number_of_completed_tasks = self.number_of_completed_tasks + 1

        if "Finished" in msg:
            self.BPBDuplicationDialog_ProgressBar.set_fraction(1)
            self.BPBDuplicationDialog_ProgressBar.set_text("{0:.0%}".format(1))
            ''' When the progress bar reaches 100%, disable the Cancel button and enable the Finish button.'''
            if len(self.failed_drives) > 0:
                self.BPBDuplicationDialog_Label.set_text \
                    ("Bit-Per-Bit Duplication Result: Checksum discrepancies found!\n"
                     "Review QA Report for further details.")
                self.BPBDuplicationDialog_Image.set_from_file(
                    str(Path(__file__).parent.absolute()) + "/res/caution-sign-128.png")
            else:
                self.BPBDuplicationDialog_Label.set_text("Bit-Per-Bit Duplication Result:\n"
                                                         "Verification completed and no discrepancies found!")
                self.BPBDuplicationDialog_Image.set_from_file(
                    str(Path(__file__).parent.absolute()) + "/res/check-128.png")
            self.BPBDuplicationDialog_FinishButton.set_sensitive(True)
            self.BPBDuplicationDialog_CancelButton.set_sensitive(False)
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
            self.BPBDuplicationDialog_CancelSpinner.start()
            self.BPBDuplicationDialog_CancelButton.set_sensitive(False)
            self.BPBDuplicationDialog_Label.set_text("Canceling...")
            return True
        if "terminate" in msg:
            """ Terminate main sub-process bpb_duplication_process() """
            while self.bpb_duplication_proc.is_alive():
                self.bpb_duplication_proc.terminate()
            self.bpb_duplication_proc.close()
            return True
        if "destroy" in msg:
            self.manager.shutdown()
            del self.manager
            while self.cancel_proc.is_alive():
                self.cancel_proc.terminate()
            self.cancel_proc.close()
            self.BPBDuplicationDialog.destroy()
        return True

    def stop_io_watch(self, source, condition):
        assert self.stop_parent.poll()
        try:
            msg = self.stop_parent.recv()
        except EOFError:
            return False

        if "spinner" in msg:
            """ Disable Cancel button since we need time to stop everyone """
            self.BPBDuplicationDialog_CancelSpinner.start()
            self.BPBDuplicationDialog_CancelButton.set_sensitive(False)
            return True
        if "terminate" in msg:
            """ Terminate main sub-process secure_erase_process() """
            while self.bpb_duplication_proc.is_alive():
                self.bpb_duplication_proc.terminate()
            self.bpb_duplication_proc.close()
            return True
        if "stop" in msg:
            self.manager.shutdown()
            del self.manager
            while self.stop_proc.is_alive():
                self.stop_proc.terminate()
            self.stop_parent.close()
            self.BPBDuplicationDialog_CancelSpinner.stop()
            self.BPBDuplicationDialog_FinishButton.set_label("Close")
            self.BPBDuplicationDialog_FinishButton.set_sensitive(True)
            return True
        return True

    def on_BPBDuplicationDialog_CancelButton_clicked(self, widget, user_data=None):
        """ Handler for BPBDuplicationDialog_CancelButton.clicked. """
        self.cancel_proc.start()

    def on_BPBDuplicationDialog_FinishButton_clicked(self, widget, user_data=None):
        """ Handler for BPBDuplicationDialog_FinishButton.clicked. """
        self.manager.shutdown()
        del self.manager
        while self.bpb_duplication_proc.is_alive():
            self.bpb_duplication_proc.terminate()
        self.bpb_duplication_proc.close()
        self.BPBDuplicationDialog.destroy()

    def on_BPBDuplicationDialog_QAButton_clicked(self, widget, user_data=None):
        """ Handler for BPBDuplicationDialog_QAButton.clicked. """
        logging.debug("abs_blkdevs length = {} abs_blkdevs = {}".format(len(self.failed_drives), self.failed_drives))
        EZDuplicator.QADialog.QADialog("Bit-Per-Bit Duplication\nQA Results",
                                       "The following drives failed\nto image or pass checksum integrity check.",
                                       self.failed_drives)
