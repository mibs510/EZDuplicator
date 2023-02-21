"""

Copyright (c) 2021 Connor McMillan <connor@mcmillan.website>. All rights reserved.

This work is licensed under the terms of the MIT license.
For a copy, see <https://opensource.org/licenses/MIT>.

"""
import logging
import os
import sys
from multiprocessing import Process, Pipe
from pathlib import Path

from gi import require_version as gi_require_version

import EZDuplicator.AboutDialog
import EZDuplicator.AppCrashedDialog
import EZDuplicator.BPBOverWriteDialog
import EZDuplicator.CapacityDetailsDialog
import EZDuplicator.ConfirmAppRestartDialog
import EZDuplicator.ConfirmPowerOffDialog
import EZDuplicator.ConfirmRebootDialog
import EZDuplicator.DataCollectionConsentDialog
import EZDuplicator.DataOnlyOverwriteDialog
import EZDuplicator.DebugDialog
import EZDuplicator.FeatureNotYetImplementedDialog
import EZDuplicator.lib.App
import EZDuplicator.lib.EZDuplicator
import EZDuplicator.NoInternetDialog
import EZDuplicator.SecureEraseDialog_1
import EZDuplicator.SettingsDialog
import EZDuplicator.VerificationOption_Dialog
import EZDuplicator.WTHDialog
import EZDuplicator.UpdateDialog

gi_require_version('Gtk', '3.0')
from gi.repository import Gtk, GLib, Gdk


class App(Gtk.ApplicationWindow):
    """ Main window with all components. """

    def __init__(self, debug=False):
        Gtk.ApplicationWindow.__init__(self, title="EZ Duplicator", window_position=Gtk.WindowPosition.CENTER_ALWAYS)
        self.builder = Gtk.Builder()
        gladefile = str(Path(__file__).parent.absolute()) + '/res/window.ui'
        if not os.path.exists(gladefile):
            # Look for glade file in this project's directory.
            gladefile = os.path.join(sys.path[0], gladefile)

        try:
            self.builder.add_objects_from_file(
                gladefile,
                [
                    'AppMenuPopover',
                    'BPBDuplication',
                    'DataOnlyDuplication',
                    'DateandTime',
                    'RestartPopover',
                    'SecureErase',
                    'UtilitiesPopover',
                    'Verify',
                    'buttons',
                    'numberOfusbs',
                    'waves',
                    'winMain',
                    'winMainUSBLogo',
                ]
            )
        except Exception as ex:
            logging.error(ex)
            sys.exit(1)

        # Get gui objects
        self.BPBDuplication = self.builder.get_object('BPBDuplication')
        self.DataOnlyDuplication = self.builder.get_object('DataOnlyDuplication')
        self.DateandTime = self.builder.get_object('DateandTime')
        self.MainMenu = self.builder.get_object('MainMenu')
        self.MainMenuButton = self.builder.get_object('MainMenuButton')
        self.SecureErase = self.builder.get_object('SecureErase')
        self.UtilitiesPopover = self.builder.get_object('UtilitiesPopover')
        self.numberOfusbs = self.builder.get_object('numberOfusbs')
        self.winMain = self.builder.get_object('winMain')
        self.winMainUSBLogo = self.builder.get_object('winMainUSBLogo')

        self.winMain.set_position(Gtk.WindowPosition.CENTER_ALWAYS)
        self.winMain.fullscreen()
        self.winMain.maximize()

        self.winMain.connect("destroy", Gtk.main_quit)
        self.builder.connect_signals(self)
        self.winMain.show_all()
        """ Splash Screen """
        """ This could probably be implemented elsewhere in a more official manner. """
        os.system("mplayer -vo gl -fs expand=1920:1080 {}".format(EZDuplicator.lib.EZDuplicator.__splash_animation__))

        """ Keep record of pids """
        self.pids = []
        self.pids.append(os.getpid())

        """ Create temp directories """
        EZDuplicator.lib.EZDuplicator.mkdir("/tmp/mnt")
        EZDuplicator.lib.EZDuplicator.mkdir("/tmp/mnt/target")
        EZDuplicator.lib.EZDuplicator.mkdir("/tmp/mnt/source")

        """ Do not execute the following if the application is in debug mode """
        if not debug:
            EZDuplicator.DataCollectionConsentDialog.DataCollectionConsentDialog()
            if not os.path.exists(EZDuplicator.lib.EZDuplicator.__ports_map__) \
                    or not os.path.exists(EZDuplicator.lib.EZDuplicator.__mounts_map__):
                EZDuplicator.WTHDialog.WTHDialog("Port/Mount map does not exist!\n"
                                                 "Refer to the MAC book at https://help.ezduplicator.com\n"
                                                 "for proper software configuration.")
                logging.warning(
                    "Software is improperly configured. Refer to the MAC book at https://help.ezduplicator.com")

        ''' Start processes '''
        ''' Update date, time, and the number of connected USBs on the upper righthand corner '''
        try:
            self.date_and_time_parent, self.date_and_time_child = Pipe(duplex=False)
            self.update_date_and_time_proc = Process(target=EZDuplicator.lib.App.update_date_and_time_daemon,
                                                     args=(self.date_and_time_child,), daemon=True,
                                                     name="EZDuplicator-Update-Date-And-Time")
            self.update_date_and_time_proc.start()
            self.pids.append(self.update_date_and_time_proc.pid)
            self.date_and_time_child.close()
            GLib.io_add_watch(self.date_and_time_parent.fileno(), GLib.IO_IN, self.date_and_time_io_watch)

            self.update_number_of_usbs_parent, self.update_number_of_usbs_child = Pipe(duplex=False)
            self.update_number_of_usbs_proc = Process(target=EZDuplicator.lib.App.update_number_of_usbs_daemon,
                                                      args=(self.update_number_of_usbs_child,), daemon=True,
                                                      name="EZDuplicator-Update-Number-Of-Targets")
            self.update_number_of_usbs_proc.start()
            self.pids.append(self.update_number_of_usbs_proc.pid)
            self.update_number_of_usbs_child.close()
            GLib.io_add_watch(self.update_number_of_usbs_parent.fileno(), GLib.IO_IN,
                              self.update_number_of_usbs_io_watch)

            self.webtail_http_server_proc = Process(target=EZDuplicator.lib.App.webtail_http_server_daemon, daemon=True,
                                                    name="EZDuplicator-Webtail-Server")
            self.webtail_http_server_proc.start()
            self.pids.append(self.webtail_http_server_proc.pid)

            if not debug:
                self.heartbeat_watchdog_parent, self.heartbeat_watchdog_child = Pipe(duplex=False)
                self.heartbeat_watchdog_proc = Process(target=EZDuplicator.lib.App.heartbeat_watchdog_daemon,
                                                       args=(self.heartbeat_watchdog_child,), daemon=True,
                                                       name="EZDuplicator-Heartbeat-Watchdog")
                self.heartbeat_watchdog_proc.start()
                self.pids.append(self.heartbeat_watchdog_proc.pid)
                self.heartbeat_watchdog_child.close()
                GLib.io_add_watch(self.heartbeat_watchdog_parent.fileno(), GLib.IO_IN,
                                  self.heartbeat_watchdog_io_watch)
        except Exception as ex:
            logging.error(ex)

    def date_and_time_io_watch(self, source, condition):
        assert self.date_and_time_parent.poll()
        try:
            i = self.date_and_time_parent.recv()
        except EOFError:
            return False
        self.DateandTime.set_text("{}".format(i))
        return True

    def update_number_of_usbs_io_watch(self, source, condition):
        assert self.update_number_of_usbs_parent.poll()
        try:
            i = self.update_number_of_usbs_parent.recv()
        except EOFError:
            return False
        response = i.split('\n')
        self.numberOfusbs.set_text(response[0])

        if "True" in response[1]:
            self.winMainUSBLogo.set_from_file(
                str(Path(__file__).parent.absolute()) + '/res/media-removable-symbolic-red.svg')
            self.numberOfusbs.override_color(Gtk.StateFlags.NORMAL, Gdk.RGBA(216, 0, 0))
        elif "False" in response[1]:
            self.winMainUSBLogo.set_from_file(
                str(Path(__file__).parent.absolute()) + '/res/media-removable-symbolic.svg')
            self.numberOfusbs.override_color(Gtk.StateFlags.NORMAL, Gdk.RGBA(255, 255, 255))

        return True

    def heartbeat_watchdog_io_watch(self, source, condition):
        assert self.heartbeat_watchdog_parent.poll()
        try:
            i = self.heartbeat_watchdog_parent.recv()
        except EOFError:
            return False

        if "Exception" in i:
            EZDuplicator.AppCrashedDialog.AppCrashedDialog()
        return True

    def on_AppMenuPopover_About_button_press_event(self, widget, user_data=None):
        """ Handler for on_AppMenuPopover_About_button_press_event. """
        EZDuplicator.AboutDialog.AboutDialog(self.winMain)

    def on_AppMenuPopover_Debug_button_press_event(self, widget, user_data=None):
        """ Handler for on_AppMenuPopover_Debug_button_press_event. """
        EZDuplicator.DebugDialog.DebugDialog(self.winMain)

    def on_RestartPopover_System_button_press_event(self, widget, user_data=None):
        """ Handler for on_RestartPopover_System_button_press_event. """
        EZDuplicator.ConfirmRebootDialog.ConfirmRebootDialog(self.winMain)

    def on_RestartPopover_Application_button_press_event(self, widget, user_data=None):
        """ Handler for on_RestartPopover_Application_button_press_event. """
        EZDuplicator.ConfirmAppRestartDialog.ConfirmAppRestarDialog(self.pids, self.winMain)

    def on_AppMenuPopover_Settings_button_press_event(self, widget, user_data=None):
        """ Handler for on_AppMenuPopover_Settings_button_press_event. """
        EZDuplicator.SettingsDialog.SettingsDialog(self.winMain)

    def on_AppMenuPopover_Shutdown_button_press_event(self, widget, user_data=None):
        """ Handler for on_AppMenuPopover_Shutdown_button_press_event. """
        EZDuplicator.ConfirmPowerOffDialog.ConfirmPowerOffDialog(self.winMain)

    def on_AppMenuPopover_Update_button_press_event(self, widget, user_data=None):
        """ Handler for on_AppMenuPopover_Update_button_press_event. """
        if EZDuplicator.lib.EZDuplicator.has_internet_connection():
            EZDuplicator.UpdateDialog.UpdateDialog(self.pids, self.winMain)
        else:
            EZDuplicator.NoInternetDialog.NoInternetDialog(self.winMain)

    def on_BPBDuplication_clicked(self, widget, user_data=None):
        """ Handler for BPBDuplication.clicked. """
        EZDuplicator.BPBOverWriteDialog.BPBOverWriteDialog()

    def on_DataOnlyDuplication_clicked(self, widget, user_data=None):
        """ Handler for DataOnlyDuplication.clicked. """
        EZDuplicator.DataOnlyOverwriteDialog.DataOnlyOverwriteDialog()

    def on_SecureErase_clicked(self, widget, user_data=None):
        """ Handler for SecureErase.clicked. """
        EZDuplicator.SecureEraseDialog_1.SecureEraseDialog_1("SecureErase")

    def on_UtilitiesPopover_Capacity_Details_button_press_event(self, widget, user_data=None):
        """ Handler for on_UtilitiesPopover_Capacity_Details_button_press_event. """
        EZDuplicator.CapacityDetailsDialog.CapacityDetailsDialog()

    def on_Verify_clicked(self, widget, user_data=None):
        """ Handler for Verify.clicked. """
        EZDuplicator.VerificationOption_Dialog.VerificationOption_Dialog()
