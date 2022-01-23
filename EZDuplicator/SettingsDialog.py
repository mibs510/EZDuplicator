"""

Copyright (c) 2021 Connor McMillan <connor@mcmillan.website>. All rights reserved.

This work is licensed under the terms of the MIT license.
For a copy, see <https://opensource.org/licenses/MIT>.

"""
import configparser
import subprocess
import glob
import logging
import multiprocessing
import os
import sys
from multiprocessing import Process
from pathlib import Path

from gi import require_version as gi_require_version

import EZDuplicator.UtilitiesDialog
import EZDuplicator.InvalidUserInputDialog
import EZDuplicator.NoInternetDialog
import EZDuplicator.WTHDialog
import EZDuplicator.lib.Settings
import EZDuplicator.lib.EZDuplicator
import EZDuplicator.UnlockSettingsDialog

gi_require_version('Gtk', '3.0')

from gi.repository import Gtk, GLib


class SettingsDialog(Gtk.ApplicationWindow):
    """ Main window with all components. """

    def __init__(self, parent):
        Gtk.ApplicationWindow.__init__(self)
        self.builder = Gtk.Builder()
        gladefile = str(Path(__file__).parent.absolute()) + '/res/window.ui'
        if not os.path.exists(gladefile):
            # Look for glade file in this project's directory.
            gladefile = os.path.join(sys.path[0], gladefile)

        try:
            self.builder.add_objects_from_file(
                gladefile,
                [
                    'DebugUtilities',
                    'DefaultSMTPSettings_Button',
                    'DefaultSMTPSettings_Button_Spinner',
                    'Email_CheckButton',
                    'ImproveSoftware_CheckButton',
                    'Network_Settings_Button',
                    'Rec_Email_Address_Entry',
                    'Repo',
                    'SMTP_Host_Entry',
                    'SMTP_Password_Entry',
                    'SMTP_Port_Entry',
                    'SMTP_Username_Entry',
                    'SendDebugMsgSyslog_CheckButton',
                    'SettingsDialog',
                    'SettingsDialog_Cancel',
                    'SettingsDialog_FirstGrid',
                    'SettingsDialog_Save',
                    'SourceDevPath',
                    'Syslog_Host_Entry',
                    'Syslog_Port_Entry',
                    'Test_Email_Button',
                    'Test_Email_Button_Spinner',
                    'TwelveVCOMPort',
                    'UnlockButton',
                    'UnlockButton_Icon',
                    'UnlockButton_Label',
                ]
            )
        except Exception as ex:
            logging.error(ex)
            sys.exit(1)

        # Get gui objects
        self.DebugUtilities = self.builder.get_object('DebugUtilities')
        self.DefaultSMTPSettings_Button = self.builder.get_object('DefaultSMTPSettings_Button')
        self.DefaultSMTPSettings_Button_Spinner = self.builder.get_object('DefaultSMTPSettings_Button_Spinner')
        self.Email_CheckButton = self.builder.get_object('Email_CheckButton')
        self.ImproveSoftware_CheckButton = self.builder.get_object('ImproveSoftware_CheckButton')
        self.Network_Settings_Button = self.builder.get_object('Network_Settings_Button')
        self.Rec_Email_Address_Entry = self.builder.get_object('Rec_Email_Address_Entry')
        self.Repo = self.builder.get_object('Repo')
        self.SMTP_Host_Entry = self.builder.get_object('SMTP_Host_Entry')
        self.SMTP_Password_Entry = self.builder.get_object('SMTP_Password_Entry')
        self.SMTP_Port_Entry = self.builder.get_object('SMTP_Port_Entry')
        self.SMTP_Username_Entry = self.builder.get_object('SMTP_Username_Entry')
        self.SendDebugMsgSyslog_CheckButton = self.builder.get_object('SendDebugMsgSyslog_CheckButton')
        self.SettingsDialog = self.builder.get_object('SettingsDialog')
        self.SettingsDialog_Cancel = self.builder.get_object('SettingsDialog_Cancel')
        self.SettingsDialog_FirstGrid = self.builder.get_object('SettingsDialog_FirstGrid')
        self.SettingsDialog_Save = self.builder.get_object('SettingsDialog_Save')
        self.SourceDevPath = self.builder.get_object('SourceDevPath')
        self.Syslog_Host_Entry = self.builder.get_object('Syslog_Host_Entry')
        self.Syslog_Port_Entry = self.builder.get_object('Syslog_Port_Entry')
        self.Test_Email_Button = self.builder.get_object('Test_Email_Button')
        self.Test_Email_Button_Spinner = self.builder.get_object('Test_Email_Button_Spinner')
        self.TwelveVCOMPort = self.builder.get_object('TwelveVCOMPort')
        self.UnlockButton = self.builder.get_object('UnlockButton')
        self.UnlockButton_Icon = self.builder.get_object('UnlockButton_Icon')
        self.UnlockButton_Label = self.builder.get_object('UnlockButton_Label')

        self.parent = parent

        self.builder.connect_signals(self)
        self.SettingsDialog.show_all()
        self.SettingsDialog.set_transient_for(self.parent)

        self.manager = multiprocessing.Manager()
        self.default_smtp_settings = self.manager.list()
        self.exception = self.manager.Value(str, "")

        EZDuplicator.lib.EZDuplicator.create_default_config()
        self.config = configparser.ConfigParser()
        self.config.read(EZDuplicator.lib.EZDuplicator.__config_file__)

        """ Activate the value of SourceDevPath because it doesn't always exist in the filesystem """
        self.SourceDevPath.append_text(self.config['EZD App']['source_dev_path'])
        self.SourceDevPath.set_active(0)

        """ Grab a list of possible paths that could belong to the source USB port """
        dirname = "/dev/disk/by-path/pci-*-scsi*"
        for name in glob.glob(dirname):
            if name not in (os.curdir, os.pardir):
                self.full = os.path.join(dirname, name)
                if self.full != self.config['EZD App']['source_dev_path']:
                    self.SourceDevPath.append_text(self.full)

        """ Grab a list of COM ports that could belong to the 12V Power Manager"""
        i = 0
        dirname = "/dev/serial/by-id/usb*"
        for name in glob.glob(dirname):
            self.full = os.path.join(dirname, name)
            self.TwelveVCOMPort.append_text(self.full)
            if self.full == self.config['EZD App']['twelve_v_com_port']:
                self.TwelveVCOMPort.set_active(i)
            i += 1

        if self.config['EZD App']['update_repo'] == "dev":
            self.Repo.set_active(0)
        else:
            self.Repo.set_active(1)

        if self.config['EZD App']['email_enabled'] == 'True':
            self.Email_CheckButton.set_active(True)
            self.Test_Email_Button.set_sensitive(True)
        else:
            self.Rec_Email_Address_Entry.set_sensitive(False)
            self.SMTP_Host_Entry.set_sensitive(False)
            self.SMTP_Port_Entry.set_sensitive(False)
            self.SMTP_Username_Entry.set_sensitive(False)
            self.SMTP_Password_Entry.set_sensitive(False)
            self.Test_Email_Button.set_sensitive(False)
        if self.config['EZD App']['improve_software'] == 'True':
            self.ImproveSoftware_CheckButton.set_active(True)
        if self.config['EZD App']['syslog_enabled'] == 'True':
            self.SendDebugMsgSyslog_CheckButton.set_active(True)
        else:
            self.Syslog_Port_Entry.set_sensitive(False)
            self.Syslog_Host_Entry.set_sensitive(False)

        self.Rec_Email_Address_Entry.set_text(self.config['EZD App']['rec_email_address'])
        self.SMTP_Host_Entry.set_text(self.config['EZD App']['mail_host'])
        self.SMTP_Port_Entry.set_text(self.config['EZD App']['mail_port'])
        self.SMTP_Username_Entry.set_text(self.config['EZD App']['mail_username'])
        self.SMTP_Password_Entry.set_text(self.config['EZD App']['mail_password'])
        self.Syslog_Host_Entry.set_text(self.config['EZD App']['syslog_host'])
        self.Syslog_Port_Entry.set_text(self.config['EZD App']['syslog_port'])

        """ By default the following objects are disabled until unlocked """
        self.SourceDevPath.set_sensitive(False)
        self.TwelveVCOMPort.set_sensitive(False)
        self.Repo.set_sensitive(False)
        self.DebugUtilities.set_sensitive(False)

        """ Get Default SMTP Process """
        self.get_default_smtp_settings_parent, self.get_default_smtp_settings_child = multiprocessing.Pipe(duplex=False)
        self.get_default_smtp_settings_proc = Process(
            target=EZDuplicator.lib.Settings.get_default_smtp_settings_process,
            args=(self.get_default_smtp_settings_child,
                  self.default_smtp_settings, self.exception,),
            daemon=False)
        """ Do not close the child handle as stop() will not be able to communicate with stop_io_wait() """
        # self.get_default_smtp_settings_child.close()
        GLib.io_add_watch(self.get_default_smtp_settings_parent.fileno(), GLib.IO_IN,
                          self.get_default_smtp_settings_io_watch)

        """ Test Email Settings Process """
        self.test_email_settings_parent, self.test_email_settings_child = multiprocessing.Pipe(duplex=False)
        self.test_email_settings_proc = Process(target=EZDuplicator.lib.Settings.test_email_process,
                                                args=(self.test_email_settings_child, self.exception,),
                                                daemon=False)
        """ Do not close the child handle as stop() will not be able to communicate with stop_io_wait() """
        # self.test_email_settings_child.close()
        GLib.io_add_watch(self.test_email_settings_parent.fileno(), GLib.IO_IN,
                          self.test_email_settings_io_watch)

    def on_DebugUtilities_clicked(self, widget, user_data=None):
        """ Handler for DebugUtilities.clicked. """
        EZDuplicator.UtilitiesDialog.UtilitiesDialog()

    def on_DefaultSMTPSettings_Button_clicked(self, widget, user_data=None):
        """ Handler for DefaultSMTPSettings_Button.clicked. """
        try:
            if EZDuplicator.lib.EZDuplicator.has_internet_connection():
                self.get_default_smtp_settings_proc.start()
            else:
                EZDuplicator.NoInternetDialog.NoInternetDialog(self.SettingsDialog)
        except Exception as ex:
            logging.exception(ex)

    def on_Email_CheckButton_toggled(self, widget, user_data=None):
        """ Handler for on_Email_CheckButton_toggled.toggled. """
        if self.Email_CheckButton.get_active():
            self.config['EZD App']['email_enabled'] = 'True'
            self.SMTP_Host_Entry.set_sensitive(True)
            self.SMTP_Port_Entry.set_sensitive(True)
            self.SMTP_Username_Entry.set_sensitive(True)
            self.SMTP_Password_Entry.set_sensitive(True)
            self.Rec_Email_Address_Entry.set_sensitive(True)
            self.Test_Email_Button.set_sensitive(True)
        else:
            self.config['EZD App']['email_enabled'] = 'False'
            self.SMTP_Host_Entry.set_sensitive(False)
            self.SMTP_Port_Entry.set_sensitive(False)
            self.SMTP_Username_Entry.set_sensitive(False)
            self.SMTP_Password_Entry.set_sensitive(False)
            self.Rec_Email_Address_Entry.set_sensitive(False)
            self.Test_Email_Button.set_sensitive(False)

    def on_ImproveSoftware_CheckButton_toggled(self, widget, user_data=None):
        """ Handler for ImproveSoftware_CheckButton.toggled. """
        if self.ImproveSoftware_CheckButton.get_active():
            self.config['EZD App']['improve_software'] = 'True'
        else:
            self.config['EZD App']['improve_software'] = 'False'

    def on_Network_Settings_Button_clicked(self, widget, user_data=None):
        """ Handler for Network_Settings_Button.clicked. """
        # gnome_control_center = subprocess.Popen(["sudo", "gnome-control-center"],
        #                                        stderr=subprocess.PIPE, stdout=subprocess.PIPE)
        # output, error = gnome_control_center.communicate()
        os.system("sudo gnome-control-center")

    def on_Rec_Email_Address_Entry_changed(self, widget, user_data=None):
        """ Handler for on_Rec_Email_Address_Entry.changed. """
        self.config['EZD App']['rec_email_address'] = self.Rec_Email_Address_Entry.get_text()

    def on_Rec_Email_Address_Entry_focus_in_event(self, widget, event, user_data=None):
        """ Handler for Rec_Email_Address_Entry.focus-in-event. """
        subprocess.Popen("onboard")

    def on_Rec_Email_Address_Entry_focus_out_event(self, widget, event, user_data=None):
        """ Handler for Rec_Email_Address_Entry.focus-out-event. """
        subprocess.Popen(["pkill", "onboard"])

    def on_Repo_changed(self, widget, user_data=None):
        """ Handler for Repo.changed. """
        self.config['EZD App']['update_repo'] = self.Repo.get_active_id()

    def on_SMTP_Host_Entry_changed(self, widget, user_data=None):
        """ Handler for SMTP_Host_Entry.changed. """
        self.config['EZD App']['mail_host'] = self.SMTP_Host_Entry.get_text()

    def on_SMTP_Host_Entry_focus_in_event(self, widget, event, user_data=None):
        """ Handler for SMTP_Host_Entry.focus-in-event. """
        subprocess.Popen("onboard")

    def on_SMTP_Host_Entry_focus_out_event(self, widget, event, user_data=None):
        """ Handler for SMTP_Host_Entry.focus-out-event. """
        subprocess.Popen(["pkill", "onboard"])

    def on_SMTP_Password_Entry_changed(self, widget, user_data=None):
        """ Handler for SMTP_Password_Entry.changed. """
        self.config['EZD App']['mail_password'] = self.SMTP_Password_Entry.get_text()

    def on_SMTP_Password_Entry_focus_in_event(self, widget, event, user_data=None):
        """ Handler for SMTP_Password_Entry.focus-in-event. """
        subprocess.Popen("onboard")

    def on_SMTP_Password_Entry_focus_out_event(self, widget, event, user_data=None):
        """ Handler for SMTP_Password_Entry.focus-out-event. """
        subprocess.Popen(["pkill", "onboard"])

    def on_SMTP_Port_Entry_changed(self, widget, user_data=None):
        """ Handler for SMTP_Port_Entry.changed. """
        self.config['EZD App']['mail_port'] = self.SMTP_Port_Entry.get_text()

    def on_SMTP_Port_Entry_focus_in_event(self, widget, event, user_data=None):
        """ Handler for SMTP_Port_Entry.focus-in-event. """
        subprocess.Popen("onboard")

    def on_SMTP_Port_Entry_focus_out_event(self, widget, event, user_data=None):
        """ Handler for SMTP_Port_Entry.focus-out-event. """
        subprocess.Popen(["pkill", "onboard"])

    def on_SMTP_Username_Entry_changed(self, widget, user_data=None):
        """ Handler for SMTP_Username_Entry.changed. """
        self.config['EZD App']['mail_username'] = self.SMTP_Username_Entry.get_text()

    def on_SMTP_Username_Entry_focus_in_event(self, widget, event, user_data=None):
        """ Handler for SMTP_Username_Entry.focus-in-event. """
        subprocess.Popen("onboard")

    def on_SMTP_Username_Entry_focus_out_event(self, widget, event, user_data=None):
        """ Handler for SMTP_Username_Entry.focus-out-event. """
        subprocess.Popen(["pkill", "onboard"])

    def on_SendDebugMsgSyslog_CheckButton_toggled(self, widget, user_data=None):
        """ Handler for SendDebugMsgSyslog_CheckButton.toggled. """
        if self.SendDebugMsgSyslog_CheckButton.get_active():
            self.config['EZD App']['syslog_enabled'] = 'True'
            self.Syslog_Port_Entry.set_sensitive(True)
            self.Syslog_Host_Entry.set_sensitive(True)
        else:
            self.config['EZD App']['syslog_enabled'] = 'False'
            self.Syslog_Port_Entry.set_sensitive(False)
            self.Syslog_Host_Entry.set_sensitive(False)

    def on_SettingsDialog_Cancel_clicked(self, widget, user_data=None):
        """ Handler for SettingsDialog_Cancel.clicked. """
        try:
            self.kill_get_smtp_settings_process()
            self.kill_test_email_settings_process()
            self.manager.shutdown()
            del self.manager
        except Exception as ex:
            logging.error(ex)
        finally:
            self.SettingsDialog.destroy()

    def on_SettingsDialog_Save_clicked(self, widget, user_data=None):
        """ Handler for SettingsDialog_Save.clicked. """
        try:
            error_message = ""
            if self.Email_CheckButton.get_active():
                error_message = self.check_for_valid_email_settings()
            if self.SendDebugMsgSyslog_CheckButton.get_active():
                if not EZDuplicator.lib.EZDuplicator.is_valid_hostname(self.Syslog_Host_Entry.get_text()):
                    error_message = error_message + "Invalid Syslog Host: {}\n".\
                        format(self.Syslog_Host_Entry.get_text())
                if not EZDuplicator.lib.EZDuplicator.is_valid_port(self.Syslog_Port_Entry.get_text()):
                    error_message = error_message + "Invalid Syslog Port: {}\n".\
                        format(self.Syslog_Port_Entry.get_text())
            if len(error_message) > 0:
                EZDuplicator.InvalidUserInputDialog.InvalidUserInputDialog(error_message)
            else:
                self.saveConfigfile()
                self.SettingsDialog_Cancel.set_label("Close")
                self.SettingsDialog_Cancel.set_sensitive(True)
        except Exception as ex:
            logging.exception(ex)

    def on_SourceDevPath_changed(self, widget, user_data=None):
        """ Handler for SourceDevPath.changed. """
        self.config['EZD App']['source_dev_path'] = self.SourceDevPath.get_active_text()

    def on_Syslog_Host_Entry_changed(self, widget, user_data=None):
        """ Handler for Syslog_Host_Entry.changed. """
        self.config['EZD App']['syslog_host'] = self.Syslog_Host_Entry.get_text()

    def on_Syslog_Host_Entry_focus_in_event(self, widget, event, user_data=None):
        """ Handler for Syslog_Host_Entry.focus-in-event. """
        subprocess.Popen("onboard")

    def on_Syslog_Host_Entry_focus_out_event(self, widget, event, user_data=None):
        """ Handler for Syslog_Host_Entry.focus-out-event. """
        subprocess.Popen(["pkill", "onboard"])

    def on_Syslog_Port_Entry_changed(self, widget, user_data=None):
        """ Handler for Syslog_Port_Entry.changed. """
        self.config['EZD App']['syslog_port'] = self.Syslog_Port_Entry.get_text()

    def on_Syslog_Port_Entry_focus_in_event(self, widget, event, user_data=None):
        """ Handler for Syslog_Port_Entry.focus-in-event. """
        subprocess.Popen("onboard")

    def on_Syslog_Port_Entry_focus_out_event(self, widget, event, user_data=None):
        """ Handler for Syslog_Port_Entry.focus-out-event. """
        subprocess.Popen(["pkill", "onboard"])

    def on_Test_Email_Button_clicked(self, widget, user_data=None):
        """ Handler for Test_SMS_Button.clicked. """
        error_message = self.check_for_valid_email_settings()
        if len(error_message) == 0:
            self.saveConfigfile()
            if EZDuplicator.lib.EZDuplicator.has_internet_connection():
                self.test_email_settings_proc.start()
            else:
                EZDuplicator.NoInternetDialog.NoInternetDialog(self.SettingsDialog)
        else:
            EZDuplicator.InvalidUserInputDialog.InvalidUserInputDialog(error_message)

    def on_TwelveVCOMPort_changed(self, widget, user_data=None):
        """ Handler for TwelveVCOMPort.changed. """
        if self.TwelveVCOMPort.get_active_text() is not None:
            self.config['EZD App']['twelve_v_com_port'] = self.TwelveVCOMPort.get_active_text()

    def on_UnlockButton_clicked(self, widget, user_data=None):
        """ Handler for UnlockButton.clicked. """
        if EZDuplicator.lib.EZDuplicator.has_internet_connection():
            EZDuplicator.UnlockSettingsDialog.UnlockSettingsDialog(self, self.SettingsDialog)
        else:
            EZDuplicator.NoInternetDialog.NoInternetDialog(self.SettingsDialog)

    def saveConfigfile(self):
        with open(EZDuplicator.lib.EZDuplicator.__config_file__, 'w') as configfile:
            self.config.write(configfile)

    def check_for_valid_email_settings(self):
        error_message = ""
        if not EZDuplicator.lib.EZDuplicator.is_valid_email(self.Rec_Email_Address_Entry.get_text()):
            error_message = error_message + "Invalid Recipient Email Address: {}\n". \
                format(self.Rec_Email_Address_Entry.get_text())
        if not EZDuplicator.lib.EZDuplicator.is_valid_hostname(self.SMTP_Host_Entry.get_text()):
            error_message = error_message + "Invalid SMTP Host: {}\n".format(self.SMTP_Host_Entry.get_text())
        if not EZDuplicator.lib.EZDuplicator.is_valid_port(self.SMTP_Port_Entry.get_text()):
            error_message = error_message + "Invalid SMTP Port: {}\n".format(self.SMTP_Port_Entry.get_text())
        if not EZDuplicator.lib.EZDuplicator.is_valid_email(self.SMTP_Username_Entry.get_text()):
            error_message = error_message + "Invalid SMTP Username: {}\n".format(
                self.SMTP_Username_Entry.get_text())
        return error_message

    def get_default_smtp_settings_io_watch(self, source, condition):
        assert self.get_default_smtp_settings_parent.poll()
        try:
            msg = self.get_default_smtp_settings_parent.recv()
        except EOFError:
            return False

        if msg == "self.DefaultSMTPSettings_Button_Spinner.start()":
            self.SettingsDialog_Save.set_sensitive(False)
            self.DefaultSMTPSettings_Button.set_sensitive(False)
            self.Test_Email_Button.set_sensitive(False)
            self.DefaultSMTPSettings_Button_Spinner.start()
            return True

        if msg == "self.config":
            mail_host = self.default_smtp_settings[0]
            mail_port = self.default_smtp_settings[1]
            mail_username = self.default_smtp_settings[2]
            mail_password = self.default_smtp_settings[3]

            self.config['EZD App']['mail_host'] = mail_host
            self.config['EZD App']['mail_port'] = mail_port
            self.config['EZD App']['mail_username'] = mail_username
            self.config['EZD App']['mail_password'] = mail_password
            return True

        if msg == "self.set_text()":
            self.SMTP_Host_Entry.set_text(self.config['EZD App']['mail_host'])
            self.SMTP_Port_Entry.set_text(self.config['EZD App']['mail_port'])
            self.SMTP_Username_Entry.set_text(self.config['EZD App']['mail_username'])
            self.SMTP_Password_Entry.set_text(self.config['EZD App']['mail_password'])
            return True

        if msg == "self.DefaultSMTPSettings_Button_Spinner.stop()":
            self.SettingsDialog_Save.set_sensitive(True)
            self.DefaultSMTPSettings_Button.set_sensitive(True)
            self.Test_Email_Button.set_sensitive(True)
            self.DefaultSMTPSettings_Button_Spinner.stop()
            self.reset_get_default_smtp_settings_process()
            return True

        if msg == "EZDuplicator.get_secret().Exception":
            EZDuplicator.WTHDialog.WTHDialog(self.exception.get())
            self.SettingsDialog_Save.set_sensitive(True)
            self.DefaultSMTPSettings_Button.set_sensitive(True)
            self.Test_Email_Button.set_sensitive(True)
            self.DefaultSMTPSettings_Button_Spinner.stop()
            self.reset_get_default_smtp_settings_process()
            return True

        return True

    def reset_get_default_smtp_settings_process(self):
        self.kill_get_smtp_settings_process()
        self.default_smtp_settings[:] = []
        self.exception.set("")
        self.get_default_smtp_settings_proc = Process(
            target=EZDuplicator.lib.Settings.get_default_smtp_settings_process,
            args=(self.get_default_smtp_settings_child, self.default_smtp_settings, self.exception,), daemon=False)

    def kill_get_smtp_settings_process(self):
        while self.get_default_smtp_settings_proc.is_alive():
            self.get_default_smtp_settings_proc.terminate()
        self.get_default_smtp_settings_proc.close()

    def get_default_smtp_settings_clean_up(self):
        self.kill_get_smtp_settings_process()
        self.manager.shutdown()
        del self.manager
        self.SettingsDialog.destroy()

    def test_email_settings_io_watch(self, source, condition):
        assert self.test_email_settings_parent.poll()
        try:
            msg = self.test_email_settings_parent.recv()
        except EOFError:
            return False

        if msg == "self.Test_Email_Button_Spinner.start()":
            self.SettingsDialog_Save.set_sensitive(False)
            self.Test_Email_Button.set_sensitive(False)
            self.DefaultSMTPSettings_Button.set_sensitive(False)
            self.Test_Email_Button_Spinner.start()
            return True

        if msg == "self.Test_Email_Button_Spinner.stop()":
            self.SettingsDialog_Save.set_sensitive(True)
            self.Test_Email_Button.set_sensitive(True)
            self.DefaultSMTPSettings_Button.set_sensitive(True)
            self.Test_Email_Button_Spinner.stop()
            self.reset_test_email_settings_process()
            return True

        if msg == "EZDuplicator.send_email_notification().Exception":
            EZDuplicator.WTHDialog.WTHDialog(self.exception.get())
            self.SettingsDialog_Save.set_sensitive(True)
            self.Test_Email_Button.set_sensitive(True)
            self.DefaultSMTPSettings_Button.set_sensitive(True)
            self.Test_Email_Button_Spinner.stop()
            self.reset_test_email_settings_process()
            return True

        return True

    def reset_test_email_settings_process(self):
        self.kill_test_email_settings_process()
        self.exception.set("")
        self.test_email_settings_proc = Process(target=EZDuplicator.lib.Settings.test_email_process,
                                                args=(self.test_email_settings_child, self.exception,),
                                                daemon=False)

    def kill_test_email_settings_process(self):
        while self.test_email_settings_proc.is_alive():
            self.test_email_settings_proc.terminate()
        self.test_email_settings_proc.close()

    def test_email_settings_clean_up(self):
        self.kill_test_email_settings_process()
        self.manager.shutdown()
        del self.manager
        self.SettingsDialog.destroy()
