"""

Copyright (c) 2021 Connor McMillan <connor@mcmillan.website>. All rights reserved.

This work is licensed under the terms of the MIT license.
For a copy, see <https://opensource.org/licenses/MIT>.

"""
import logging
import os
import shutil
import time

import EZDuplicator.lib.EZDuplicator


def upload_process(pipe_connection, exception):
    pipe_connection.send("self.ConsentDialog_AcceptSpinner.start()")
    zip_file = "/tmp/{}-{}".format(EZDuplicator.lib.EZDuplicator.get_serial_number(), time.strftime('%m_%d_%y_%I%M%S'))
    try:
        shutil.make_archive(zip_file, 'zip', EZDuplicator.lib.EZDuplicator.__log_dir__)
        download_link = EZDuplicator.lib.EZDuplicator.upload_file("{}.zip".format(zip_file))
        EZDuplicator.lib.EZDuplicator.send_cs_email_notification(
            EZDuplicator.lib.EZDuplicator.get_serial_number(), download_link)
        if os.path.isfile("{}.zip".format(zip_file)):
            os.remove("{}.zip".format(zip_file))
    except Exception as ex:
        logging.exception(ex)
        exception.set(str(ex))
        pipe_connection.send("WTHDialog.WTHDialog()")
        if os.path.isfile("{}.zip".format(zip_file)):
            os.remove("{}.zip".format(zip_file))
    finally:
        pipe_connection.send("self.ConsentDialog_AcceptSpinner.stop()")

