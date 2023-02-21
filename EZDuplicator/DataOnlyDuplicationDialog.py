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
import EZDuplicator.lib.DataOnlyDuplication
import EZDuplicator.lib.weresync.daemon.device
import EZDuplicator.lib.weresync.exception
import EZDuplicator.lib.weresync.plugins
import EZDuplicator.lib.EZDuplicator
import EZDuplicator.WTHDialog

gi_require_version('Gtk', '3.0')


class DataOnlyDuplicationDialog(Gtk.Dialog):
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
                    'DataOnlyDuplicationDialog',
                    'DataOnlyDuplicationDialog_CancelButton',
                    'DataOnlyDuplicationDialog_CancelSpinner',
                    'DataOnlyDuplicationDialog_FinishButton',
                    'DataOnlyDuplicationDialog_Image',
                    'DataOnlyDuplicationDialog_Label',
                    'DataOnlyDuplicationDialog_ProgressBar',
                    'DataOnlyDuplicationDialog_QAButton',
                    'DataOnlyDuplication_LargeDataDetected',
                ]
            )
        except Exception as ex:
            logging.error(ex)
            sys.exit(1)

        # Get gui objects
        self.DataOnlyDuplicationDialog = self.builder.get_object('DataOnlyDuplicationDialog')
        self.DataOnlyDuplicationDialog_CancelButton = self.builder.get_object('DataOnlyDuplicationDialog_CancelButton')
        self.DataOnlyDuplicationDialog_CancelSpinner = \
            self.builder.get_object('DataOnlyDuplicationDialog_CancelSpinner')
        self.DataOnlyDuplicationDialog_FinishButton = self.builder.get_object('DataOnlyDuplicationDialog_FinishButton')
        self.DataOnlyDuplicationDialog_Image = self.builder.get_object('DataOnlyDuplicationDialog_Image')
        self.DataOnlyDuplicationDialog_Image.set_from_animation(
            GdkPixbuf.PixbufAnimation.new_from_file(str(Path(__file__).parent.absolute()) + "/res/file-128.gif"))
        self.DataOnlyDuplicationDialog_Label = self.builder.get_object('DataOnlyDuplicationDialog_Label')
        self.DataOnlyDuplicationDialog_ProgressBar = self.builder.get_object('DataOnlyDuplicationDialog_ProgressBar')
        self.DataOnlyDuplicationDialog_QAButton = self.builder.get_object('DataOnlyDuplicationDialog_QAButton')
        self.DataOnlyDuplication_LargeDataDetected = self.builder.get_object('DataOnlyDuplication_LargeDataDetected')
        self.DataOnlyDuplicationDialog.show_all()
        self.builder.connect_signals(self)

        """ Hide this hint unless if lib.Verification.verification_process() emits a signal """
        self.DataOnlyDuplication_LargeDataDetected.set_visible(False)

        """ duplication_task_manager() + partclone_task_manager() + qa_task_manager() + grab checksums from source
            + clean the source partitions + cleanup + some extras so not to reach 100% until told do so """
        self.source_by_path = EZDuplicator.lib.EZDuplicator.get_config_setting('source_dev_path')
        self.number_of_usbs = EZDuplicator.lib.EZDuplicator.get_number_or_list_of_usbs('number', self.source_by_path)
        self.number_of_tasks = ((self.number_of_usbs * 3) + 5)
        self.number_of_completed_tasks = 0
        self.manager = multiprocessing.Manager()
        self.failed_drives = self.manager.list()
        self.pids = self.manager.list()

        """ Cancel Process """
        self.cancel_parent, self.cancel_child = multiprocessing.Pipe(duplex=False)
        self.cancel_proc = Process(target=EZDuplicator.lib.DataOnlyDuplication.cancel,
                                   args=(self.number_of_usbs, self.pids, self.cancel_child), daemon=False)
        """ Do not close the child handle as cancel() will not be able to communicate with cancel_io_wait() """
        # self.update_child.close()
        GLib.io_add_watch(self.cancel_parent.fileno(), GLib.IO_IN, self.cancel_io_watch)

        """ Stop Process """
        self.stop_parent, self.stop_child = multiprocessing.Pipe(duplex=False)
        self.stop_proc = Process(target=EZDuplicator.lib.DataOnlyDuplication.stop,
                                 args=(self.pids, self.stop_child), daemon=False)
        """ Do not close the child handle as stop() will not be able to communicate with stop_io_wait() """
        # self.upload_child.close()
        GLib.io_add_watch(self.stop_parent.fileno(), GLib.IO_IN, self.stop_io_watch)

        """ Main Process """
        """ Disable the finish & QA results button until we actually finish duplicating drives. """
        self.DataOnlyDuplicationDialog_FinishButton.set_sensitive(False)
        self.DataOnlyDuplicationDialog_QAButton.set_sensitive(False)

        """ Begin duplicating drives """
        """ 2 task per usb (one duplication & one qa) + 1 task to grab xxhsum hashes from source drive. """
        self.data_only_duplication_process_parent, self.data_only_duplication_process_child = \
            multiprocessing.Pipe(duplex=False)
        self.data_only_duplication_proc = \
            Process(target=EZDuplicator.lib.DataOnlyDuplication.data_only_duplication_process,
                    args=(self.data_only_duplication_process_child, self.pids,
                          self.failed_drives), daemon=False)
        self.data_only_duplication_proc.start()
        self.data_only_duplication_process_child.close()
        GLib.io_add_watch(self.data_only_duplication_process_parent.fileno(), GLib.IO_IN,
                          self.data_only_duplication_process_io_watch)

    def data_only_duplication_process_io_watch(self, source, condition):
        assert self.data_only_duplication_process_parent.poll()
        try:
            msg = self.data_only_duplication_process_parent.recv()
        except EOFError:
            return False

        if "Bump" in msg:
            self.number_of_completed_tasks = self.number_of_completed_tasks + 1
            progress = (self.number_of_completed_tasks / self.number_of_tasks)
            """ Bounce it back down to the maximum 100% if needed """
            if progress > 1:
                logging.info("progress = {}, so reassigning to 1".format(progress))
                progress = 1
            self.DataOnlyDuplicationDialog_ProgressBar.set_fraction(progress)
            self.DataOnlyDuplicationDialog_ProgressBar.set_text("{0:.0%}".format(progress))
            return True

        if "Cleanup" in msg:
            self.DataOnlyDuplicationDialog_ProgressBar.set_fraction(.99)
            self.DataOnlyDuplicationDialog_ProgressBar.set_text("{0:.0%}".format(.99))

        if "Enable_QADialog_Button" in msg:
            self.DataOnlyDuplicationDialog_QAButton.set_sensitive(True)
            return True

        if "LargeDataDetected" in msg:
            self.DataOnlyDuplication_LargeDataDetected.set_visible(True)

        if "Stop" in msg:
            self.stop_proc.start()
            self.DataOnlyDuplicationDialog_Label.set_text("Fatal Error: Review debug console for further details.\n"
                                                          "Possible faulty source/targets.")
            self.DataOnlyDuplicationDialog_Image.set_from_file(
                str(Path(__file__).parent.absolute()) + "/res/red-warning-128.png")
            return True

        if "Finished" in msg:
            self.DataOnlyDuplicationDialog_ProgressBar.set_fraction(1)
            self.DataOnlyDuplicationDialog_ProgressBar.set_text("{0:.0%}".format(1))
            ''' When the progress bar reaches 100%, disable the Cancel button and enable the Finish button.'''
            if len(self.failed_drives) > 0:
                self.DataOnlyDuplicationDialog_Label.set_text(
                    "Data Only Duplication Result: Issues encountered while duplicating\n"
                    "or checksum discrepancies found!\nReview QA Report for further details.")
                self.DataOnlyDuplicationDialog_Image.set_from_file(
                    str(Path(__file__).parent.absolute()) + "/res/caution-sign-128.png")
                self.DataOnlyDuplicationDialog_QAButton.set_sensitive(True)
            else:
                self.DataOnlyDuplicationDialog_Label.set_text("Data Only Duplication Result:\n"
                                                              "Verification completed and no discrepancies found!")
                self.DataOnlyDuplicationDialog_Image.set_from_file(
                    str(Path(__file__).parent.absolute()) + "/res/check-128.png")
            self.DataOnlyDuplicationDialog_FinishButton.set_sensitive(True)
            self.DataOnlyDuplicationDialog_CancelButton.set_sensitive(False)
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
            self.DataOnlyDuplicationDialog_CancelSpinner.start()
            self.DataOnlyDuplicationDialog_CancelButton.set_sensitive(False)
            self.DataOnlyDuplicationDialog_Label.set_text("Cancelling...")
            return True
        if "terminate" in msg:
            """ Terminate main sub-process data_only_duplication_process() """
            logging.info("Terminating main process (data_only_duplication_proc)...")
            while self.data_only_duplication_proc.is_alive():
                self.data_only_duplication_proc.terminate()
            self.data_only_duplication_proc.close()
            logging.info("Finished terminating main process (data_only_duplication_proc)...")
            return True
        if "destroy" in msg:
            logging.info("Terminating multiprocessing.Manager() process...")
            self.manager.shutdown()
            del self.manager
            logging.info("Terminating cancel_proc...")
            while self.cancel_proc.is_alive():
                self.cancel_proc.terminate()
            self.cancel_proc.close()
            logging.info("Destroying DataOnlyDuplicationDialog...")
            self.DataOnlyDuplicationDialog.destroy()
        return True

    def stop_io_watch(self, source, condition):
        assert self.stop_parent.poll()
        try:
            msg = self.stop_parent.recv()
        except EOFError:
            return False

        if "spinner" in msg:
            """ Disable Cancel button since we need time to stop everyone """
            self.DataOnlyDuplicationDialog_CancelSpinner.start()
            self.DataOnlyDuplicationDialog_CancelButton.set_sensitive(False)
            return True
        if "terminate" in msg:
            """ Terminate main sub-process data_only_duplication_process() """
            logging.info("Terminating main process (data_only_duplication_proc)...")
            while self.data_only_duplication_proc.is_alive():
                self.data_only_duplication_proc.terminate()
            self.data_only_duplication_proc.close()
            logging.info("Finished terminating main process (data_only_duplication_proc)...")
            return True
        if "stop" in msg:
            logging.info("Terminating stop_proc...")
            while self.stop_proc.is_alive():
                self.stop_proc.terminate()
            self.stop_parent.close()
            self.DataOnlyDuplicationDialog_CancelSpinner.stop()
            self.DataOnlyDuplicationDialog_FinishButton.set_label("Close")
            self.DataOnlyDuplicationDialog_FinishButton.set_sensitive(True)
            return True
        return True

    def on_DataOnlyDuplicationDialog_CancelButton_clicked(self, widget, user_data=None):
        """ Handler for DataOnlyDuplicationDialog_CancelButton.clicked. """
        self.cancel_proc.start()

    def on_DataOnlyDuplicationDialog_FinishButton_clicked(self, widget, user_data=None):
        """ Handler for DataOnlyDuplicationDialog_FinishButton.clicked. """
        try:
            self.manager.shutdown()
            del self.manager
            while self.data_only_duplication_proc.is_alive():
                self.data_only_duplication_proc.terminate()
            self.data_only_duplication_proc.close()
        except Exception as ex:
            logging.error(ex)
        finally:
            self.DataOnlyDuplicationDialog.destroy()

    def on_DataOnlyDuplicationDialog_QAButton_clicked(self, widget, user_data=None):
        """ Handler for DataOnlyDuplicationDialog_QAButton.clicked. """
        current_number_of_usbs = EZDuplicator.lib.EZDuplicator.get_number_or_list_of_usbs('number', self.source_by_path)
        if current_number_of_usbs != self.number_of_usbs:
            EZDuplicator.WTHDialog.WTHDialog("Error: Cannot render map, targets were removed!")
        else:
            EZDuplicator.QADialog.QADialog("Data Only Duplication\nQA Results",
                                           "The following drives failed\nto image or pass checksum integrity check.",
                                           self.failed_drives)
