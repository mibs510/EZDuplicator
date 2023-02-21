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
import EZDuplicator.lib.DataOnlyDuplication
import EZDuplicator.lib.Verification
import EZDuplicator.lib.weresync.daemon.device
import EZDuplicator.lib.weresync.exception
import EZDuplicator.lib.EZDuplicator
import EZDuplicator.WTHDialog

gi_require_version('Gtk', '3.0')


class VerificationDialog(Gtk.Dialog):
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
                    'VerificationDialog',
                    'VerificationDialog_CancelButton',
                    'VerificationDialog_CancelSpinner',
                    'VerificationDialog_FinishButton',
                    'VerificationDialog_Image',
                    'VerificationDialog_Label',
                    'VerificationDialog_LargeDataDetected',
                    'VerificationDialog_ProgressBar',
                    'VerificationDialog_QAButton',
                ]
            )
        except Exception as ex:
            logging.exception(ex)
            sys.exit(1)

        # Get gui objects
        self.VerificationDialog = self.builder.get_object('VerificationDialog')
        self.VerificationDialog_CancelButton = self.builder.get_object('VerificationDialog_CancelButton')
        self.VerificationDialog_CancelSpinner = self.builder.get_object('VerificationDialog_CancelSpinner')
        self.VerificationDialog_FinishButton = self.builder.get_object('VerificationDialog_FinishButton')
        self.VerificationDialog_Image = self.builder.get_object('VerificationDialog_Image')
        self.VerificationDialog_Image.set_from_animation(
            GdkPixbuf.PixbufAnimation.new_from_file(
                str(Path(__file__).parent.absolute()) + "/res/ab-testing-128.gif"))
        self.VerificationDialog_Label = self.builder.get_object('VerificationDialog_Label')
        self.VerificationDialog_LargeDataDetected = self.builder.get_object('VerificationDialog_LargeDataDetected')
        self.VerificationDialog_ProgressBar = self.builder.get_object('VerificationDialog_ProgressBar')
        self.VerificationDialog_QAButton = self.builder.get_object('VerificationDialog_QAButton')
        self.builder.connect_signals(self)
        self.VerificationDialog.show_all()

        """ Hide this hint unless if lib.Verification.verification_process() emits a signal """
        self.VerificationDialog_LargeDataDetected.set_visible(False)

        self.source_by_path = EZDuplicator.lib.EZDuplicator.get_source_by_path()
        self.number_of_usbs = EZDuplicator.lib.EZDuplicator.get_number_or_list_of_usbs('number', self.source_by_path)
        self.number_of_tasks = self.number_of_usbs + 1
        self.number_of_completed_tasks = 0
        self.manager = multiprocessing.Manager()
        self.failed_drives = self.manager.list()
        self.pids = self.manager.list()
        self.option = option

        """ Cancel Process """
        self.cancel_parent, self.cancel_child = multiprocessing.Pipe(duplex=False)
        self.cancel_proc = Process(target=EZDuplicator.lib.Verification.cancel,
                                   args=(self.number_of_usbs, self.pids, self.cancel_child), daemon=False)
        """ Do not close the child handle as update_io_watch() will not be able to communicate with cancel_io_wait() """
        # self.update_child.close()
        GLib.io_add_watch(self.cancel_parent.fileno(), GLib.IO_IN, self.cancel_io_watch)

        """ Stop Process """
        self.stop_parent, self.stop_child = multiprocessing.Pipe(duplex=False)
        self.stop_proc = Process(target=EZDuplicator.lib.Verification.stop,
                                 args=(self.pids, self.stop_child), daemon=False)
        """ Do not close the child handle as stop() will not be able to communicate with stop_io_wait() """
        # self.upload_child.close()
        GLib.io_add_watch(self.stop_parent.fileno(), GLib.IO_IN, self.stop_io_watch)

        """ Main Process """
        """ Disable the finish & QA results button until we actually finish duplicating drives. """
        self.VerificationDialog_FinishButton.set_sensitive(False)
        self.VerificationDialog_QAButton.set_sensitive(False)

        """ Begin duplicating drives """
        """ 2 task per usb (one duplication & one qa) + 1 task to grab xxhsum hashes from source drive. """
        self.verification_parent, self.verification_child = multiprocessing.Pipe(duplex=False)
        self.verification_proc = Process(target=EZDuplicator.lib.Verification.verification_process,
                                         args=(self.verification_child, self.pids, self.failed_drives, self.option),
                                         daemon=False)
        self.verification_proc.start()
        self.verification_child.close()
        GLib.io_add_watch(self.verification_parent.fileno(), GLib.IO_IN, self.verification_process_io_watch)

    def verification_process_io_watch(self, source, condition):
        assert self.verification_parent.poll()
        try:
            msg = self.verification_parent.recv()
        except EOFError:
            return False

        if "Bump" in msg:
            self.number_of_completed_tasks = self.number_of_completed_tasks + 1
            progress = (self.number_of_completed_tasks / self.number_of_tasks)
            """ Bounce it back down to the maximum 100% if needed """
            if progress > 1:
                logging.info("progress = {}, so reassigning to 1".format(progress))
                progress = 1
            self.VerificationDialog_ProgressBar.set_fraction(progress)
            self.VerificationDialog_ProgressBar.set_text("{0:.0%}".format(progress))
            return True

        if "Cleanup" in msg:
            self.VerificationDialog_ProgressBar.set_fraction(.99)
            self.VerificationDialog_ProgressBar.set_text("{0:.0%}".format(.99))

        if "Enable_QADialog_Button" in msg:
            self.VerificationDialog_QAButton.set_sensitive(True)
            return True

        if "LargeDataDetected" in msg:
            self.VerificationDialog_LargeDataDetected.set_visible(True)

        if "Stop" in msg:
            self.stop_proc.start()
            self.VerificationDialog_Label.set_text("Fatal Error: Review debug console for further details.\n"
                                                   "Possible faulty source/targets.")
            self.VerificationDialog_Image.set_from_file(
                str(Path(__file__).parent.absolute()) + "/res/red-warning-128.png")
            return True

        self.number_of_completed_tasks = self.number_of_completed_tasks + 1

        if "Finished" in msg:
            self.VerificationDialog_ProgressBar.set_fraction(1)
            self.VerificationDialog_ProgressBar.set_text("{0:.0%}".format(1))
            ''' When the progress bar reaches 100%, disable the Cancel button and enable the Finish button.'''
            if len(self.failed_drives) > 0:
                self.VerificationDialog_Label.set_text(
                    "Verification Result: Discrepancies found!\nReview QA Report for further details.")
                self.VerificationDialog_Image.set_from_file(
                    str(Path(__file__).parent.absolute()) + "/res/caution-sign-128.png")
                self.VerificationDialog_QAButton.set_sensitive(True)
            else:
                self.VerificationDialog_Label.set_text("Verification Result: No discrepancies found!\n")
                self.VerificationDialog_Image.set_from_file(
                    str(Path(__file__).parent.absolute()) + "/res/check-128.png")
            self.VerificationDialog_FinishButton.set_sensitive(True)
            self.VerificationDialog_CancelButton.set_sensitive(False)
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
            self.VerificationDialog_CancelSpinner.start()
            self.VerificationDialog_CancelButton.set_sensitive(False)
            self.VerificationDialog_Label.set_text("Cancelling...")
            return True
        if "terminate" in msg:
            """ Terminate main sub-process verification_process() """
            while self.verification_proc.is_alive():
                self.verification_proc.terminate()
            self.verification_proc.close()
            return True
        if "destroy" in msg:
            self.manager.shutdown()
            del self.manager
            while self.cancel_proc.is_alive():
                self.cancel_proc.terminate()
            self.cancel_proc.close()
            self.VerificationDialog.destroy()
        return True

    def stop_io_watch(self, source, condition):
        assert self.stop_parent.poll()
        try:
            msg = self.stop_parent.recv()
        except EOFError:
            return False

        if "spinner" in msg:
            """ Disable Cancel button since we need time to stop everyone """
            self.VerificationDialog_CancelSpinner.start()
            self.VerificationDialog_CancelButton.set_sensitive(False)
            return True
        if "terminate" in msg:
            """ Terminate main sub-process secure_erase_process() """
            while self.verification_proc.is_alive():
                self.verification_proc.terminate()
            self.verification_proc.close()
            return True
        if "stop" in msg:
            while self.stop_proc.is_alive():
                self.stop_proc.terminate()
            self.stop_proc.close()
            self.VerificationDialog_CancelSpinner.stop()
            self.VerificationDialog_FinishButton.set_label("Close")
            self.VerificationDialog_FinishButton.set_sensitive(True)
            return True
        return True

    def on_VerificationDialog_CancelButton_clicked(self, widget, user_data=None):
        """ Handler for VerificationDialog_CancelButton.clicked. """
        self.cancel_proc.start()

    def on_VerificationDialog_FinishButton_clicked(self, widget, user_data=None):
        """ Handler for VerificationDialog_FinishButton.clicked. """
        try:
            self.manager.shutdown()
            del self.manager
            while self.verification_proc.is_alive():
                self.verification_proc.terminate()
            self.verification_proc.close()
        except Exception as ex:
            logging.error(ex)
        finally:
            self.VerificationDialog.destroy()

    def on_VerificationDialog_QAButton_clicked(self, widget, user_data=None):
        """ Handler for VerificationDialog_QAButton.clicked. """
        current_number_of_usbs = EZDuplicator.lib.EZDuplicator.get_number_or_list_of_usbs('number', self.source_by_path)
        if current_number_of_usbs != self.number_of_usbs:
            EZDuplicator.WTHDialog.WTHDialog("Error: Cannot render map, targets were removed!")
        else:
            EZDuplicator.QADialog.QADialog("Verification QA Results",
                                           "The following drives have checksum\n"
                                           "mismatches when compared to the source.",
                                           self.failed_drives)
