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

import EZDuplicator.BPBDuplicationDialog
import EZDuplicator.DataOnlyDuplicationDialog
import EZDuplicator.ErrorEncounteredDialog
import EZDuplicator.PowerCyclePortsDialog
import EZDuplicator.QADialog
import EZDuplicator.SecureEraseDialog_2
import EZDuplicator.VerificationDialog
import EZDuplicator.lib.Connect2Hub
import EZDuplicator.lib.weresync.daemon.device

gi_require_version('Gtk', '3.0')

from gi.repository import Gtk, GLib


class Connect2HubDialog(Gtk.Dialog):
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
                    'Connect2HubDialog',
                    'Connect2HubDialog_CancelButton',
                    'Connect2HubDialog_ContinueButton',
                    'Connect2HubDialog_ContinueSpinner',
                    'NoUSBsFoundInfoBar',
                    'NoUSBsFoundInfoBar_Message',
                ]
            )
        except Exception as ex:
            logging.error(ex)
            sys.exit(1)

        # Get gui objects
        self.Connect2HubDialog = self.builder.get_object('Connect2HubDialog')
        self.Connect2HubDialog_CancelButton = self.builder.get_object('Connect2HubDialog_CancelButton')
        self.Connect2HubDialog_ContinueButton = self.builder.get_object('Connect2HubDialog_ContinueButton')
        self.Connect2HubDialog_ContinueSpinner = self.builder.get_object('Connect2HubDialog_ContinueSpinner')
        self.NoUSBsFoundInfoBar = self.builder.get_object('NoUSBsFoundInfoBar')
        self.NoUSBsFoundInfoBar_Message = self.builder.get_object('NoUSBsFoundInfoBar_Message')
        self.Connect2HubDialog.show_all()
        self.builder.connect_signals(self)
        self.option = option
        self.manager = multiprocessing.Manager()
        self.abort = self.manager.Value(bool, False)
        self.below_average_targets = self.manager.list()
        self.out_of_bound = self.manager.list()

        """ Let's hide the info bar until needed """
        self.NoUSBsFoundInfoBar.hide()

        """ Continue Process """
        self.continue_parent, self.continue_child = multiprocessing.Pipe(duplex=False)
        self.continue_proc = Process(target=EZDuplicator.lib.Connect2Hub.continue_process,
                                     args=(self.continue_child, self.option, self.abort, self.below_average_targets,
                                           self.out_of_bound,),
                                     daemon=False)
        """ Do not close the child handle as stop() will not be able to communicate with stop_io_wait() """
        # self.get_default_smtp_settings_child.close()
        GLib.io_add_watch(self.continue_parent.fileno(), GLib.IO_IN, self.continue_io_watch)

    def on_Connect2HubDialog_CancelButton_clicked(self, widget, user_data=None):
        """ Handler for Connect2HubDialog_CancelButton.clicked. """
        self.clean_up()

    def on_Connect2HubDialog_ContinueButton_clicked(self, widget, user_data=None):
        """ Handler for Connect2HubDialog_ContinueButton.clicked. """
        self.continue_proc.start()

    def on_NoUSBsFoundInfoBar_response(self, widget, response_id, user_data=None):
        """ Handler for NoUSBsFoundInfoBar.response. """
        self.NoUSBsFoundInfoBar.hide()

    def reset_continue_process(self):
        while self.continue_proc.is_alive():
            self.continue_proc.terminate()
        self.continue_proc.close()
        self.abort.set(False)
        self.below_average_targets[:] = []
        self.out_of_bound[:] = []
        self.continue_proc = Process(target=EZDuplicator.lib.Connect2Hub.continue_process,
                                     args=(self.continue_child, self.option, self.abort, self.below_average_targets,
                                           self.out_of_bound),
                                     daemon=False)

    def kill_continue_process(self):
        try:
            while self.continue_proc.is_alive():
                self.continue_proc.terminate()
            self.continue_proc.close()
        except Exception as ex:
            logging.exception(ex)

    def clean_up(self):
        try:
            self.kill_continue_process()
            self.manager.shutdown()
            del self.manager
            self.Connect2HubDialog.destroy()
        except Exception as ex:
            logging.exception(ex)
        finally:
            self.Connect2HubDialog.destroy()

    def continue_io_watch(self, source, condition):
        assert self.continue_parent.poll()
        try:
            msg = self.continue_parent.recv()
        except EOFError:
            return False

        if msg == "self.Connect2HubDialog_ContinueSpinner.start()":
            self.Connect2HubDialog_ContinueButton.set_sensitive(False)
            self.Connect2HubDialog_ContinueSpinner.start()
            return True

        if msg == "self.Connect2HubDialog_ContinueSpinner.stop()":
            self.Connect2HubDialog_ContinueSpinner.stop()
            self.Connect2HubDialog_ContinueButton.set_sensitive(True)
            return True

        if msg == "self.NoUSBsFoundInfoBar.show()":
            self.NoUSBsFoundInfoBar.show()
            self.Connect2HubDialog_ContinueSpinner.stop()
            self.reset_continue_process()
            return True

        if msg == "EZDuplicator.PowerCyclePortsDialog.PowerCyclePortsDialog()":
            EZDuplicator.PowerCyclePortsDialog.PowerCyclePortsDialog(self.Connect2HubDialog)
            self.Connect2HubDialog_ContinueSpinner.stop()
            self.reset_continue_process()
            return True

        if msg == "SecureEraseDialog_2.SecureEraseDialog_2()":
            EZDuplicator.SecureEraseDialog_2.SecureEraseDialog_2()
            self.clean_up()
            return True

        if msg == "check_for_defective_targets.QADialog.QADialog()":
            EZDuplicator.QADialog.QADialog("Data Only Duplication\nPre-Duplication Check",
                                           "One or more targets are not equal in capacity with neighboring targets."
                                           "\nAll targets are required to have a homogenous advertised capacity.",
                                           self.below_average_targets)
            self.clean_up()
            return True

        if msg == "BPBDuplicationDialog.BPBDuplicationDialog()":
            EZDuplicator.BPBDuplicationDialog.BPBDuplicationDialog()
            self.clean_up()
            return True

        if msg == "self.NoUSBsFoundInfoBar_Message.set_text(source_not_detected)":
            self.NoUSBsFoundInfoBar_Message.set_text(
                "Source media not detected!\nPlease insert source media into the designated port.")
            self.NoUSBsFoundInfoBar.show()
            self.Connect2HubDialog_ContinueSpinner.stop()
            self.reset_continue_process()
            return True

        if msg == "check_for_valid_partition_table.ErrorEncounteredDialog.ErrorEncounteredDialog()":
            logging.warning("Refer to https://help.ezduplicator.com/books/knowledge-base/page/partition-table-types-win"
                            "dows-vs-linux")
            EZDuplicator.ErrorEncounteredDialog.ErrorEncounteredDialog(
                "The source device does not have a\n supported partition type.",
                str(Path(__file__).parent.absolute()) + "/res/partition-table-type-qr-code.svg")
            self.clean_up()
            return True

        if msg == "check_for_out_of_boundary.QADialog().ErrorEncounteredDialog()":
            logging.warning("Refer to https://help.ezduplicator.com/books/knowledge-base/page/advertised-capacity")
            EZDuplicator.QADialog.QADialog("Data Only Duplication\nPre-Duplication Check",
                                           "One or more drives do not have enough space for all the partitions of "
                                           "the source."
                                           "\nThe partitions of the source may require to be shrinked.",
                                           self.out_of_bound)
            EZDuplicator.ErrorEncounteredDialog.ErrorEncounteredDialog(
                "Partitions of the source are larger than the size of the "
                "targets.\nScan the QR code below to learn more.",
                str(Path(__file__).parent.absolute()) + "/res/advertised-capacity-qr-code.svg")
            self.clean_up()
            return True

        if msg == "check_filesystem_support.ErrorEncounteredDialog.ErrorEncounteredDialog()":
            logging.warning("Refer to https://help.ezduplicator.com/books/qa/page/what-is-and-what-is-not-supported-by-"
                            "data-only-duplication")
            EZDuplicator.ErrorEncounteredDialog.ErrorEncounteredDialog(
                "The source contains non-supported filesystem.\nScan the QR code below to learn more.",
                str(Path(__file__).parent.absolute()) + "/res/what-is-supported-by-data-only-duplication.svg")
            self.clean_up()
            return True

        if msg == "DataOnlyDuplicationDialog.DataOnlyDuplicationDialog()":
            EZDuplicator.DataOnlyDuplicationDialog.DataOnlyDuplicationDialog()
            self.clean_up()
            return True

        if msg == "VerificationDialog.VerificationDialog(BPBVerification)":
            EZDuplicator.VerificationDialog.VerificationDialog("BPBVerification")
            self.clean_up()
            return True

        if msg == "VerificationDialog.VerificationDialog(DataOnlyVerification)":
            EZDuplicator.VerificationDialog.VerificationDialog("DataOnlyVerification")
            self.clean_up()
            return True

        return True
