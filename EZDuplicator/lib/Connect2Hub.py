"""

Copyright (c) 2021 Connor McMillan <connor@mcmillan.website>. All rights reserved.

This work is licensed under the terms of the MIT license.
For a copy, see <https://opensource.org/licenses/MIT>.

"""
import logging

import EZDuplicator.lib.weresync.daemon.device
import EZDuplicator.lib.weresync.exception
import EZDuplicator.lib.EZDuplicator
import EZDuplicator.lib.DataOnlyDuplication


def continue_process(pipe_connection, option, abort, below_average_targets, out_of_bound):
    pipe_connection.send("self.Connect2HubDialog_ContinueSpinner.start()")

    source_by_path = EZDuplicator.lib.EZDuplicator.get_config_setting('source_dev_path')
    source = EZDuplicator.lib.EZDuplicator.get_source_blkdev(source_by_path)
    source_dev_manager = EZDuplicator.lib.weresync.daemon.device.DeviceManager(source, "/mnt")
    usbs = EZDuplicator.lib.EZDuplicator.get_number_or_list_of_usbs('list', source_by_path)
    get_number_of_usbs_response = EZDuplicator.lib.EZDuplicator.get_number_or_list_of_usbs('number', source_by_path,
                                                                                           warnings=True)
    number_of_targets = int(get_number_of_usbs_response.split('\n')[0])
    logging.debug("number_of_targets = {}".format(number_of_targets))
    warning_flag = get_number_of_usbs_response.split('\n')[1]
    logging.debug("warning_flag = {}".format(warning_flag))

    if number_of_targets <= 0:
        pipe_connection.send("self.NoUSBsFoundInfoBar.show()")
    elif warning_flag == "True":
        pipe_connection.send("EZDuplicator.PowerCyclePortsDialog.PowerCyclePortsDialog()")
    else:
        if option == 'SecureErase':
            pipe_connection.send("SecureEraseDialog_2.SecureEraseDialog_2()")
        elif option == 'BPBDuplication':
            if EZDuplicator.lib.EZDuplicator.is_source_connected(
                    EZDuplicator.lib.EZDuplicator.get_config_setting('source_dev_path')):
                """ Preliminary checks """
                check_for_defective_targets(pipe_connection, usbs, abort, below_average_targets)
                if not abort.get():
                    pipe_connection.send("BPBDuplicationDialog.BPBDuplicationDialog()")
            else:
                pipe_connection.send("self.NoUSBsFoundInfoBar_Message.set_text(source_not_detected)")
        elif option == 'DataOnlyDuplication':
            if EZDuplicator.lib.EZDuplicator.is_source_connected(
                    EZDuplicator.lib.EZDuplicator.get_config_setting('source_dev_path')):
                """ Preliminary checks """
                check_for_valid_partition_table(pipe_connection, source_dev_manager, abort)
                check_for_out_of_boundary(pipe_connection, abort, source, source_dev_manager, usbs, out_of_bound)
                check_filesystem_support(pipe_connection, abort, source_dev_manager)
                check_for_defective_targets(pipe_connection, usbs, abort, below_average_targets)

                if not abort.get():
                    pipe_connection.send("DataOnlyDuplicationDialog.DataOnlyDuplicationDialog()")
            else:
                pipe_connection.send("self.NoUSBsFoundInfoBar_Message.set_text(source_not_detected)")
        elif option == 'BPBVerification' or option == 'DataOnlyVerification':
            if EZDuplicator.lib.EZDuplicator.is_source_connected(
                    EZDuplicator.lib.EZDuplicator.get_config_setting('source_dev_path')):
                if option == 'BPBVerification':
                    pipe_connection.send("VerificationDialog.VerificationDialog(BPBVerification)")
                if option == 'DataOnlyVerification':
                    pipe_connection.send("VerificationDialog.VerificationDialog(DataOnlyVerification)")
            else:
                pipe_connection.send("self.NoUSBsFoundInfoBar_Message.set_text(source_not_detected)")


def check_for_valid_partition_table(pipe_connection, source_manager, abort):
    try:
        source_manager.get_partition_table_type()
    except EZDuplicator.lib.weresync.exception.UnsupportedDeviceError as ex:
        abort.set(True)
        logging.error(ex)
        pipe_connection.send("check_for_valid_partition_table.ErrorEncounteredDialog.ErrorEncounteredDialog()")


def check_for_out_of_boundary(pipe_connection, abort, source, source_manager, targets, out_of_bound):
    """ Check each partition from the source and compare it to the targets.
         The byte count of the entire drive must be less than or equal to the lowest"""
    try:
        size_of_all_source_partitions_in_bytes = 0
        for part in source_manager.get_partitions():
            size_of_all_source_partitions_in_bytes = size_of_all_source_partitions_in_bytes + \
                                                     EZDuplicator.lib.EZDuplicator.get_size_in_bytes(source + str(part))

        for usb in targets:
            if size_of_all_source_partitions_in_bytes > EZDuplicator.lib.EZDuplicator.get_size_in_bytes(usb):
                out_of_bound.append(usb)
        if len(out_of_bound) > 0:
            logging.error("Partitions of the source are larger than the capacity of the targets.")
            abort.set(True)
            pipe_connection.send("check_for_out_of_boundary.QADialog().ErrorEncounteredDialog()")
    except Exception as ex:
        logging.error(ex)


def check_filesystem_support(pipe_connection, abort, source_manager):
    """ Check to see if the partitions are supported by partclone """
    for partition in source_manager.get_partitions():
        file_system = source_manager.get_partition_file_system(partition)
        if file_system is not None and file_system != "swap" and file_system not in \
                EZDuplicator.lib.DataOnlyDuplication.SUPPORTED_FILESYSTEM_TYPES:
            abort.set(True)
            logging.error("The source contains non-supported partitions.")
            pipe_connection.send("check_filesystem_support.ErrorEncounteredDialog.ErrorEncounteredDialog()")


def check_for_defective_targets(pipe_connection, targets, abort, below_average_targets):
    size_of_targets = []
    for usb in targets:
        size_of_targets.append(EZDuplicator.lib.EZDuplicator.get_size_in_bytes(usb))

    smallest_target_in_bytes = min(size_of_targets)

    """ Sometime a drives marked as 32GB could actually have a faulty NAND chip that has an actual capacity of 10GB 
        We need to compare the drive with the lowest byte count against the average bytecount of all targets combined. 
    """
    average_target_in_bytes = round(sum(size_of_targets) / len(size_of_targets))
    if smallest_target_in_bytes < average_target_in_bytes:
        """ Find all targets that are less than the average and show the operator 
            which targets are halting the operation"""

        for usb in targets:
            if EZDuplicator.lib.EZDuplicator.get_size_in_bytes(usb) < average_target_in_bytes:
                below_average_targets.append(usb)
        logging.error("One or more drives are not equal in capacity with neighboring targets."
                      "All targets are required to have a homogenous advertised capacity.")
        logging.debug("below_average_targets = {}".format(below_average_targets))
        pipe_connection.send("check_for_defective_targets.QADialog.QADialog()")
        abort.set(True)
