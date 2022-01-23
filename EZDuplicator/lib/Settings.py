"""

Copyright (c) 2021 Connor McMillan <connor@mcmillan.website>. All rights reserved.

This work is licensed under the terms of the MIT license.
For a copy, see <https://opensource.org/licenses/MIT>.

"""
import logging

import EZDuplicator.lib.EZDuplicator


def get_default_smtp_settings_process(pipe_connection, default_smtp_settings, exception):
    try:
        pipe_connection.send("self.DefaultSMTPSettings_Button_Spinner.start()")
        try:
            default_smtp_settings.append(EZDuplicator.lib.EZDuplicator.get_secret('mail_host'))
            default_smtp_settings.append(EZDuplicator.lib.EZDuplicator.get_secret('mail_port'))
            default_smtp_settings.append(EZDuplicator.lib.EZDuplicator.get_secret('mail_username'))
            default_smtp_settings.append(EZDuplicator.lib.EZDuplicator.get_secret('mail_password'))
        except Exception as ex:
            logging.error(ex)
            exception.set(str(ex))
            pipe_connection.send("self.DefaultSMTPSettings_Button_Spinner.stop()")
            pipe_connection.send("EZDuplicator.get_secret().Exception")
            EZDuplicator.lib.EZDuplicator.sleep_indfinite()

        pipe_connection.send("self.config")
        pipe_connection.send("self.set_text()")
        pipe_connection.send("self.DefaultSMTPSettings_Button_Spinner.stop()")
    except Exception as ex:
        logging.error(ex)


def test_email_process(pipe_connection, exception):
    try:
        pipe_connection.send("self.Test_Email_Button_Spinner.start()")
        try:
            EZDuplicator.lib.EZDuplicator.send_email_notification(None, None, None, test=True)
        except Exception as ex:
            logging.error(ex)
            exception.set(str(ex))
            pipe_connection.send("self.Test_Email_Button_Spinner.stop()")
            pipe_connection.send("EZDuplicator.send_email_notification().Exception")
            EZDuplicator.lib.EZDuplicator.sleep_indfinite()

        pipe_connection.send("self.Test_Email_Button_Spinner.stop()")
    except Exception as ex:
        logging.error(ex)
