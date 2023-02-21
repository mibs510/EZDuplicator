"""

Copyright (c) 2021 Connor McMillan <connor@mcmillan.website>. All rights reserved.

This work is licensed under the terms of the MIT license.
For a copy, see <https://opensource.org/licenses/MIT>.

"""
import glob
import json
import logging
import multiprocessing
import os
import queue
import resource
import subprocess
import sys
import tempfile
import time
from multiprocessing import Process, Queue, current_process
from pathlib import Path
from time import sleep

import EZDuplicator.lib.weresync.daemon.device
import EZDuplicator.lib.weresync.exception
import EZDuplicator.lib.EZDuplicator

SUPPORTED_FILESYSTEM_TYPES = []
for partclone in glob.glob("/*/partclone.*"):
    utils = partclone.split("/")[2]
    file_system = utils.split(".")[1]
    SUPPORTED_FILESYSTEM_TYPES.append(file_system)

SUPPORTED_FSCK_FILESYSTEM_TYPES = []
for fsck in glob.glob("/*/fsck.*"):
    utils = fsck.split("/")[2]
    file_system = utils.split(".")[1]
    SUPPORTED_FILESYSTEM_TYPES.append(file_system)


def data_only_duplication_process(pipe_connection, pids, failed_drives):
    logging.info("================== Begin Data Only Duplication ==================")
    source_by_path = EZDuplicator.lib.EZDuplicator.get_source_by_path()
    source = EZDuplicator.lib.EZDuplicator.get_source_blkdev(source_by_path)
    targets = EZDuplicator.lib.EZDuplicator.get_number_or_list_of_usbs('list', source_by_path)
    number_of_targets = EZDuplicator.lib.EZDuplicator.get_number_or_list_of_usbs('number', source_by_path)
    processes = []
    number_of_processes = multiprocessing.cpu_count() * 2
    tasks_to_accomplish = Queue()
    tasks_that_are_done = Queue()

    """ Unmount everything """
    # logging.info("Starting to unmount each source and target...")
    # EZDuplicator.lib.DataOnlyDuplication.unmount_all_partitions(source)
    # for target in targets:
    #     EZDuplicator.lib.DataOnlyDuplication.unmount_all_partitions(target)
    # logging.info("Finished unmounting each source and target.")

    """ Clean mount(8) map """
    logging.info("Starting to clean mount points from mount(8)...")
    clean_mount_map()
    logging.info("Finished cleaning mount points from mount(8).")

    """ Clean the source """
    logging.info("Starting to clean source...")
    EZDuplicator.lib.DataOnlyDuplication.fsck(source)
    pipe_connection.send("Bump")
    logging.info("Finished cleaning source.")

    """ Mount the source """
    logging.info("Mounting all source partitions.")
    EZDuplicator.lib.DataOnlyDuplication.mount_all_source_partitions(source)
    logging.info("Finished mounting all source partitions.")

    """ Enable the hint if the total used space on the source exceeds more than 250MB """
    if EZDuplicator.lib.DataOnlyDuplication.get_size_of_used_space(source) > 250000000:
        pipe_connection.send("LargeDataDetected")

    """ Check the source for a bootloader """
    # boot_partition = None
    # syslinux = None
    # grub = None
    # prefix = source.split("/")[2] + "_"
    # temp_source = tempfile.mkdtemp(dir="/tmp/mnt/source", prefix=prefix)
    # source_manager = EZDuplicator.lib.weresync.daemon.device.DeviceManager(source, temp_source)

    # excluded_partitions = []
    # for partition in source_manager.get_partitions():
    #     file_system = source_manager.get_partition_file_system(partition)
    #     if file_system is None or file_system == "swap":
    #         excluded_partitions.append(file_system)

    # syslinux = \
    #     lib.weresync.plugins.search_for_boot_part(temp_source, source_manager, "syslinux", excluded_partitions)
    # grub = lib.weresync.plugins.search_for_boot_part(temp_source, source_manager, "grub", excluded_partitions)

    # if syslinux is not None and grub is not None:
    #     logging.warning("Two bootloaders (grub & syslinux) found on the source!? ()".format(self.source))
    # elif syslinux is not None and grub is None:
    #     boot_partition = syslinux
    # elif syslinux is None and grub is not None:
    #     boot_partition = grub
    # elif syslinux is None and grub is None:
    #     logging.info("No bootloader found on the source ({})".format(self.source))

    """ Duplication Queue """
    logging.info("<--- Begin duplication_task_manager --->")
    for target in targets:
        tasks_to_accomplish.put(target)

    # creating processes
    for x in range(number_of_processes):
        process = Process(target=EZDuplicator.lib.DataOnlyDuplication.duplication_task_manager,
                          args=(tasks_to_accomplish, tasks_that_are_done, pipe_connection, source, failed_drives,),
                          daemon=True)
        processes.append(process)
        process.start()
        pids.append(process.pid)

    for process in processes:
        process.join()

    while not tasks_that_are_done.empty():
        logging.info(tasks_that_are_done.get())

    tasks_that_are_done.close()
    tasks_to_accomplish.close()
    logging.info("<--- End duplication_task_manager --->")

    """ Grab a list of the checksums in from the source drive """
    logging.info("<--- Begin get_list_of_xxhsums(source) --->")
    list_of_source_xxhsums = EZDuplicator.lib.DataOnlyDuplication.get_list_of_xxhsums(source, failed_drives)
    logging.info("<--- Begin get_list_of_xxhsums(source) --->")
    pipe_connection.send("Bump")

    """ Did we fail to get checksum(s) from the source? """
    for target in failed_drives:
        if source == target:
            logging.error("Cannot proceed! Failed to obtain checksum(s) from source!")
            pipe_connection.send("Stop")
            EZDuplicator.lib.EZDuplicator.sleep_indfinite()

    """ Unmount everything """
    EZDuplicator.lib.DataOnlyDuplication.unmount_all_partitions(source)
    # for target in targets:
    #     EZDuplicator.lib.DataOnlyDuplication.unmount_all_partitions(target)

    """ Clean mount(8) map """
    clean_mount_map()

    """ partclone Queue """
    logging.info("<--- Begin partclone_task_manager --->")
    tasks_to_accomplish = Queue()
    tasks_that_are_done = Queue()

    for target in targets:
        tasks_to_accomplish.put(target)

    for y in range(number_of_processes):
        process = Process(target=EZDuplicator.lib.DataOnlyDuplication.partclone_task_manager,
                          args=(tasks_to_accomplish, tasks_that_are_done, pipe_connection, source, failed_drives),
                          daemon=True)
        processes.append(process)
        process.start()
        pids.append(process.pid)

    for process in processes:
        process.join()

    while not tasks_that_are_done.empty():
        logging.info(tasks_that_are_done.get())

    tasks_that_are_done.close()
    tasks_to_accomplish.close()
    logging.info("<--- End partclone_task_manager --->")

    """ QA Queue """
    logging.info("<--- Begin qa_task_manager --->")
    tasks_to_accomplish = Queue()
    tasks_that_are_done = Queue()

    for target in targets:
        tasks_to_accomplish.put(target)

    for z in range(number_of_processes):
        process = Process(target=EZDuplicator.lib.DataOnlyDuplication.qa_task_manager,
                          args=(tasks_to_accomplish, tasks_that_are_done, pipe_connection, source,
                                list_of_source_xxhsums, failed_drives),
                          daemon=True)
        processes.append(process)
        process.start()
        pids.append(process.pid)

    """ Completing process """
    for process in processes:
        process.join()

    while not tasks_that_are_done.empty():
        logging.info(tasks_that_are_done.get())

    tasks_that_are_done.close()
    tasks_to_accomplish.close()
    logging.info("<--- End qa_task_manager --->")

    """ Clean up """
    logging.info("<--- Begin cleanup --->")
    pipe_connection.send("Cleanup")

    """ Kill all processes so to avoid 'resource busy' errors while trying to unmount each target"""
    EZDuplicator.lib.EZDuplicator.kill_pids(pids)

    """ Unmount everything """
    # logging.info("Starting to unmount each source and target...")
    # EZDuplicator.lib.DataOnlyDuplication.unmount_all_partitions(source)
    # for target in targets:
    #     EZDuplicator.lib.DataOnlyDuplication.unmount_all_partitions(target)
    # logging.info("Finished unmounting each source and target.")

    """ Clean mount(8) map """
    logging.info("Starting to clean mount points from mount(8)...")
    clean_mount_map()
    logging.info("Finished cleaning mount points from mount(8).")

    """ Clean up directories in /tmp/mnt/source & /tmp/mnt/target """
    EZDuplicator.lib.DataOnlyDuplication.cleanup_dirs()

    pipe_connection.send("Finished")
    logging.info("<--- End cleanup --->")

    if len(failed_drives) == 0:
        EZDuplicator.lib.EZDuplicator.send_email_notification("Data Only Duplication", "{} drive(s) duplicated".
                                                              format(number_of_targets), "Successful", test=False)
    elif len(failed_drives) > 0:
        logging.debug("number_of_failed_drives = {}, failed_drives = {}".format(len(failed_drives), failed_drives))
        pipe_connection.send("Enable_QADialog_Button")
        EZDuplicator.lib.EZDuplicator.send_email_notification("Data Only Duplication", "{}/{} drive(s) failed".
                                                              format(len(failed_drives), number_of_targets),
                                                              "Unsuccessful", test=False)
    logging.info("================== End Data Only Duplication ==================")


def cancel(number_of_usbs, pids, cancel_io_watch):
    try:
        cancel_io_watch.send("spinner")
        EZDuplicator.lib.EZDuplicator.kill_pids(pids)
        cancel_io_watch.send("terminate")

        # source_by_path = EZDuplicator.lib.EZDuplicator.get_source_by_path()
        # source = EZDuplicator.lib.EZDuplicator.get_source_blkdev(source_by_path)
        # targets = EZDuplicator.lib.EZDuplicator.get_number_or_list_of_usbs('list', source_by_path)

        # logging.info("Starting to unmount each source and target...")
        # EZDuplicator.lib.DataOnlyDuplication.unmount_all_partitions(source)
        # for target in targets:
        #     EZDuplicator.lib.DataOnlyDuplication.unmount_all_partitions(target)
        # logging.info("Finished unmounting each source and target.")

        """ Clean mount(8) map """
        logging.info("Starting to clean mount points from mount(8)...")
        clean_mount_map()
        logging.info("Finished cleaning mount points from mount(8).")

        EZDuplicator.lib.EZDuplicator.send_email_notification(
            "Data Only Duplication", "Operator aborted {} drive(s) while performing data only duplication".format(
                number_of_usbs), "Incomplete", test=False)
        cancel_io_watch.send("destroy")
    except Exception as ex:
        logging.error(ex, exc_info=sys.exc_info())


def stop(pids, stop_io_watch):
    try:
        stop_io_watch.send("spinner")
        EZDuplicator.lib.EZDuplicator.kill_pids(pids)
        stop_io_watch.send("terminate")

        # source_by_path = EZDuplicator.lib.EZDuplicator.get_source_by_path()
        # source = EZDuplicator.lib.EZDuplicator.get_source_blkdev(source_by_path)
        # targets = EZDuplicator.lib.EZDuplicator.get_number_or_list_of_usbs('list', source_by_path)

        # logging.info("Starting to unmount each source and target...")
        # EZDuplicator.lib.DataOnlyDuplication.unmount_all_partitions(source)
        # for target in targets:
        #     EZDuplicator.lib.DataOnlyDuplication.unmount_all_partitions(target)
        # logging.info("Finished unmounting each source and target.")

        """ Clean mount(8) map """
        logging.info("Starting to clean mount points from mount(8)...")
        clean_mount_map()
        logging.info("Finished cleaning mount points from mount(8).")

        EZDuplicator.lib.EZDuplicator.send_email_notification(
            "Data Only Duplication", "Review debug console for further details.",
            "Fatal Error Occured", test=False)
        stop_io_watch.send("stop")
    except Exception as ex:
        logging.error(ex, exc_info=sys.exc_info())


def duplication_task_manager(tasks_to_accomplish, tasks_that_are_done, pipe_connection, source, failed_drives):
    while True:
        try:
            '''
                try to get task from the queue. get_nowait() function will 
                raise queue.Empty exception if the queue is empty. 
                queue(False) function would do the same task also.
            '''
            task = tasks_to_accomplish.get_nowait()
            logging.info("data_only_duplication({} -> {})".format(source, task))
            """ It has been observed that low quality USB drives will lock the open.write() method.
            In doing so, it causes a memory leak/runoff until the kernel OOM (out_of_memory) decides to terminate the 
            process. This will cease the taskManager() method from putting the task in the tasks acommplished Queue.
            Py Gtk never receives signals that progress has been made and therefore the progressbar never reachs 100%. 
            TODO/WIP: Add a feature to alert operator of failed USB drives that is mapped physically by row and column
            so that appropiate actions may be taken. """
            soft, hard = resource.getrlimit(resource.RLIMIT_AS)
            """ Limit process to 256MB of RAM """
            resource.setrlimit(resource.RLIMIT_AS, (268435456, hard))

            EZDuplicator.lib.DataOnlyDuplication.data_only_duplication(source, task, pipe_connection, failed_drives)
        except queue.Empty:

            break
        except (OSError, IOError, Exception, EOFError, SystemError, RuntimeError) as ex:
            logging.error(ex)
        else:
            '''
                if no exception has been raised, add the task completion 
                message to task_that_are_done queue
            '''
            tasks_that_are_done.put(task + " was completed by " + current_process().name)
            time.sleep(.5)
    return True


def partclone_task_manager(tasks_to_accomplish, tasks_that_are_done, pipe_connection, source, list_of_failed_drives):
    while True:
        try:
            '''
                try to get task from the queue. get_nowait() function will 
                raise queue.Empty exception if the queue is empty. 
                queue(False) function would do the same task also.
            '''
            task = tasks_to_accomplish.get_nowait()
            logging.info("partclone_task_manager({} -> {})".format(source, task))
            """ It has been observed that low quality USB drives will lock the open.write() method.
            In doing so, it causes a memory leak/runoff until the kernel OOM (out_of_memory) decides to terminate the 
            process. This will cease the taskManager() method from putting the task in the tasks acommplished Queue.
            Py Gtk never receives signals that progress has been made and therefore the progressbar never reachs 100%. 
            TODO/WIP: Add a feature to alert operator of failed USB drives that is mapped physically by row and column
            so that appropiate actions may be taken. """
            soft, hard = resource.getrlimit(resource.RLIMIT_AS)
            """ Limit process to 256MB of RAM """
            resource.setrlimit(resource.RLIMIT_AS, (268435456, hard))

            EZDuplicator.lib.DataOnlyDuplication.partclone(source, task, pipe_connection, list_of_failed_drives)
        except queue.Empty:

            break
        except (OSError, IOError, Exception, EOFError, SystemError, RuntimeError) as ex:
            logging.error(ex)
        else:
            '''
                if no exception has been raised, add the task completion 
                message to task_that_are_done queue
            '''
            tasks_that_are_done.put(task + " was completed by " + current_process().name)
            time.sleep(.5)
    return True


def qa_task_manager(tasks_to_accomplish, tasks_that_are_done, pipe_connection, source, list_of_source_xxhsums,
                    list_of_failed_drives):
    while True:
        try:
            '''
                try to get task from the queue. get_nowait() function will 
                raise queue.Empty exception if the queue is empty. 
                queue(False) function would do the same task also.
            '''
            task = tasks_to_accomplish.get_nowait()
            logging.info("data_only_qa({} =? {})".format(source, task))
            """ It has been observed that low quality USB drives will lock the open.write() method.
            In doing so, it causes a memory leak/runoff until the kernel OOM (out_of_memory) decides to terminate the 
            process. This will cease the taskManager() method from putting the task in the tasks acommplished Queue.
            Py Gtk never receives signals that progress has been made and therefore the progressbar never reachs 100%. 
            TODO/WIP: Add a feature to alert operator of failed USB drives that is mapped physically by row and column
            so that appropiate actions may be taken. """
            soft, hard = resource.getrlimit(resource.RLIMIT_AS)
            """ Limit process to 256MB of RAM """
            resource.setrlimit(resource.RLIMIT_AS, (268435456, hard))

            EZDuplicator.lib.DataOnlyDuplication.data_only_qa(task, pipe_connection, list_of_failed_drives,
                                                              list_of_source_xxhsums)
        except queue.Empty:

            break
        except (OSError, IOError, Exception, EOFError, SystemError, RuntimeError) as ex:
            logging.error(ex)
        else:
            '''
                if no exception has been raised, add the task completion 
                message to task_that_are_done queue
            '''
            tasks_that_are_done.put(task + " was completed by " + current_process().name)
            time.sleep(.5)
    return True


def get_partition_table_type(source):
    """Returns a string containing the type of partition table.
    :returns: Returns a string containing the type of partition table."""
    partition_table_proc = subprocess.Popen(
        ["parted", "-s", source, "print"],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT)
    output, error = partition_table_proc.communicate()
    exit_code = partition_table_proc.returncode
    if exit_code != 0:
        raise Exception("Non-zero exit code")
    partition_table_result = str(output, "utf-8").split("\n")
    partition_table_result = str(partition_table_result[3]).split(" ")
    partition_table = partition_table_result[2]
    if partition_table == 'msdos' or partition_table == 'gpt':
        return partition_table
    else:
        raise Exception("Unsupported partition table type: {}".format(partition_table))


def set_partition_table(target, table_type):
    """Returns True on successfully creating a partition table on target or Flase if it failed.
    :returns: Returns an integer denoting success or failure"""
    partition_table_proc = subprocess.Popen(
        ["parted", "-s", target, "mktable", table_type],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT)
    output, error = partition_table_proc.communicate()
    exit_code = partition_table_proc.returncode
    if exit_code != 0:
        return False
    else:
        return True


def set_partition_table_null(target):
    try:
        with open(target, 'wb+') as usb:
            for i in range(0, 512):
                usb.write(int(0).to_bytes(1, 'big'))
    except Exception as ex:
        logging.error(ex)
        raise Exception(ex)


def get_uuid(source, partition):
    proc = subprocess.Popen(
        ["blkid", "-o", "value", source + str(partition), "-s" "UUID"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE)
    output, error = proc.communicate()
    if proc.returncode != 0:
        raise Exception("Error getting uuid (UUID). {}".format(str(error, "utf-8")))
    return str(output, "utf-8").replace("\n", "")


def get_label(source, partition):
    proc = subprocess.Popen(
        ["blkid", "-o", "value", source + str(partition), "-s" "LABEL"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE)
    output, error = proc.communicate()
    if proc.returncode != 0:
        raise Exception("Error getting volume label (LABEL). {}".format(str(error, "utf-8")))
    return str(output, "utf-8").replace("\n", "")


def get_disk_identifier(source):
    """ Returns a string containing the partition UUID (msdos). This is seen in blkid(8) as PARTUUID="..."
    :returns: Returns a string containing the partition UUID. """

    proc = subprocess.Popen(
        ["fdisk", source, "-l"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE)
    output, error = proc.communicate()
    if proc.returncode != 0:
        raise Exception("Error getting msdos disk identifier (PARTUUID). {}".format(str(error, "utf-8")))
    lines = str(output, "utf-8").split("\n")
    result = list(filter(lambda x: x.strip().startswith("Disk identifier"), lines))
    return result[0].strip().split(" ")[2]


def get_gpt_partuuid(source, partition):
    proc = subprocess.Popen(
        ["blkid", "-o", "value", source + str(partition), "-s" "PARTUUID"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE)
    output, error = proc.communicate()
    if proc.returncode != 0:
        raise Exception("Error getting GPT partition UUID (PARTUUID). {}".format(str(error, "utf-8")))
    return str(output, "utf-8").replace("\n", "")


def copy_uuids(source, target):
    source_device_manager = EZDuplicator.lib.weresync.daemon.device.DeviceManager(source)
    try:
        for partition in source_device_manager.get_partitions():
            partition = str(partition)
            filesystem = source_device_manager.get_partition_file_system(partition)
            if filesystem is not None and filesystem not in SUPPORTED_FILESYSTEM_TYPES:
                uuid = get_uuid(source, partition)
                if "ext" in filesystem:
                    proc = subprocess.Popen(
                        "tune2fs -U {} {}".format(uuid, target + partition),
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                        shell=True)
                    output, error = proc.communicate()
                    if proc.returncode != 0:
                        raise Exception("Error changing ext* uuid (UUID) on {}. {}".format(target + str(partition),
                                                                                           str(error, "utf-8")))
                elif filesystem == "btrfs":
                    proc = subprocess.Popen(
                        "btrfstune -U {} {}".format(uuid, target + partition),
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                        shell=True)
                    output, error = proc.communicate()
                    if proc.returncode != 0:
                        raise Exception("Error changing btrfs uuid (UUID) on {}. {}".format(target + str(partition),
                                                                                            str(error, "utf-8")))
                elif filesystem == "swap":
                    proc = subprocess.Popen(
                        "swaplabel -U {} {}".format(uuid, target + partition),
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                        shell=True)
                    output, error = proc.communicate()
                    if proc.returncode != 0:
                        raise Exception("Error changing swap uuid (UUID) on {}. {}".format(target + str(partition),
                                                                                           str(error, "utf-8")))
                elif filesystem == "ntfs":
                    proc = subprocess.Popen(
                        "ntfslabel --new-serial={} {}".format(uuid, target + partition),
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                        shell=True)
                    output, error = proc.communicate()
                    if proc.returncode != 0:
                        raise Exception("Error changing ntfs uuid (UUID={}) on {}. {}".format(uuid,
                                                                                              target + str(partition),
                                                                                              str(error, "utf-8")))
                elif filesystem == "fat" or filesystem == "vfat":
                    """ mlabel -N 0x3A14D173 :: -i /dev/sdb1 """
                    """ uuid = 3A14-D173 -> uuid = 3A14D173 -> uuid = 0x3A14D173 """
                    uuid = uuid.replace("-", "")
                    uuid = "0x" + uuid
                    proc = subprocess.Popen(
                        "mlabel -N {} :: -i {}".format(uuid, target + partition),
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                        shell=True)
                    output, error = proc.communicate()
                    if proc.returncode != 0:
                        raise Exception("Error changing *fat* uuid (UUID) on {}. {}".format(target + str(partition),
                                                                                            str(error, "utf-8")))
                else:
                    logging.warning("EZDuplicator does not support changing the UUID on {} filesystem.".
                                    format(file_system))
    except Exception as ex:
        logging.error(ex)


def set_gpt_disk_identifier(target, disk_identifier):
    """ Set Disk Identifier for GPT """
    """ Sanitize data """
    disk_identifier = disk_identifier.replace("\n", "")
    table_proc = subprocess.Popen(
        ["sgdisk", "-U", disk_identifier, target],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE)
    output, error = table_proc.communicate()
    if table_proc.returncode != 0:
        raise Exception("Could not set GPT disk indentifier on target device ({}) {}".format(target, output))


def copy_partuuids(source, target):
    try:
        if get_partition_table_type(source) == "msdos":
            """ Set PARTUUID """
            part_uuid = get_disk_identifier(source)
            table_proc = subprocess.Popen(
                ["fdisk", target],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                stdin=subprocess.PIPE,
                universal_newlines=True)
            output, error = table_proc.communicate(input="x\ni\n{}\nr\nw".format(part_uuid))
            if table_proc.returncode != 0:
                raise Exception("Could not set msdos PARTUUID ({}) on target device ({}). {}".
                                format(target, part_uuid, error))
        elif get_partition_table_type(source) == "gpt":
            device_manager = EZDuplicator.lib.weresync.daemon.device.DeviceManager(target)
            disk_identifier = get_disk_identifier(source)
            try:
                set_gpt_disk_identifier(target, disk_identifier)
            except Exception as ex:
                logging.error("Could not set gpt disk identifier ({}) on {}: {}".
                              format(disk_identifier, target, ex))
            for partition in device_manager.get_partitions():
                filesystem = device_manager.get_partition_file_system(partition)
                if filesystem is not None and filesystem not in SUPPORTED_FILESYSTEM_TYPES:
                    part_uuid = get_gpt_partuuid(source, partition)
                    table_proc = subprocess.Popen(["sgdisk", "-u", "{}:{}".format(str(partition), part_uuid), target],
                                                  stdout=subprocess.PIPE,
                                                  stderr=subprocess.PIPE)
                    output, error = table_proc.communicate()
                    if table_proc.returncode != 0:
                        raise Exception("Could not set gpt PARTUUID on target device ({}{}) {}".
                                        format(target, partition, error))
    except Exception as ex:
        logging.error(ex)


def copy_labels(source, target):
    target_device_manager = EZDuplicator.lib.weresync.daemon.device.DeviceManager(target)
    try:
        for partition in target_device_manager.get_partitions():
            partition = str(partition)
            filesystem = target_device_manager.get_partition_file_system(partition)
            if filesystem is not None and filesystem not in SUPPORTED_FILESYSTEM_TYPES:
                label = get_label(source, partition)
                if "ext" in filesystem:
                    proc = subprocess.Popen(
                        "tune2fs -L \"{}\" {}".format(label, target + partition),
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                        shell=True)
                    output, error = proc.communicate()
                    if proc.returncode != 0:
                        raise Exception("Error changing ext* label (LABEL). {}".format(str(error, "utf-8")))
                elif "btrfs" in filesystem:
                    proc = subprocess.Popen(
                        "btrfs filesystem label {} \"{}\"".format(target + partition, label),
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                        shell=True)
                    output, error = proc.communicate()
                    if proc.returncode != 0:
                        raise Exception("Error changing btrfs volume label (LABEL). {}".format(str(error, "utf-8")))
                elif "reiserfs" in filesystem:
                    proc = subprocess.Popen(
                        "reiserfstune -l \"{}\" {}".format(label, target + partition),
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                        shell=True)
                    output, error = proc.communicate()
                    if proc.returncode != 0:
                        raise Exception("Error changing reiserfs volume label (LABEL). {}".format(str(error, "utf-8")))
                elif "jfs" in filesystem:
                    proc = subprocess.Popen(
                        "jfs_tune -L \"{}\" {}".format(label, target + partition),
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                        shell=True)
                    output, error = proc.communicate()
                    if proc.returncode != 0:
                        raise Exception("Error changing jfs volume label (LABEL). {}".format(str(error, "utf-8")))
                elif "xfs" in filesystem:
                    proc = subprocess.Popen(
                        "xfs_admin -L \"{}\" {}".format(label, target + partition),
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                        shell=True)
                    output, error = proc.communicate()
                    if proc.returncode != 0:
                        raise Exception("Error changing jfs volume label (LABEL). {}".format(str(error, "utf-8")))
                elif "udf" in filesystem:
                    proc = subprocess.Popen(
                        "udf_label {} \"{}\"".format(target + partition, label),
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                        shell=True)
                    output, error = proc.communicate()
                    if proc.returncode != 0:
                        raise Exception("Error changing jfs volume label (LABEL). {}".format(str(error, "utf-8")))
                elif "swap" in filesystem:
                    proc = subprocess.Popen(
                        "swaplabel -L \"{}\" {}".format(label, target + partition),
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                        shell=True)
                    output, error = proc.communicate()
                    if proc.returncode != 0:
                        raise Exception("Error changing swap volume label (LABEL). {}".format(str(error, "utf-8")))
                elif "ntfs" in filesystem:
                    proc = subprocess.Popen(
                        "ntfslabel {} \"{}\"".format(target + partition, label),
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                        shell=True)
                    output, error = proc.communicate()
                    if proc.returncode != 0:
                        raise Exception("Error changing ntfs volume label (LABEL). {}".format(str(error, "utf-8")))
                elif "fat" == filesystem or "vfat" == filesystem:
                    proc = subprocess.Popen(
                        "fatlabel {} \"{}\"".format(target + partition, label),
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                        shell=True)
                    output, error = proc.communicate()
                    if proc.returncode != 0:
                        raise Exception("Error changing *fat* volume label (LABEL). {}".format(str(error, "utf-8")))
                elif "exfat" == filesystem:
                    proc = subprocess.Popen(
                        "exfatlabel {} \"{}\"".format(target + partition, label),
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                        shell=True)
                    output, error = proc.communicate()
                    if proc.returncode != 0:
                        raise Exception("Error changing exfat volume label (LABEL). {}".format(str(error, "utf-8")))
                elif "hfs" in filesystem:
                    """ There defintely is better way to implement this and the most obvious way is to include it 
                    into weresync (set_partition_file_system()) """
                    mkfs_proc = subprocess.Popen(["mkfs." + filesystem, "-v", label, target + partition],
                                                 stdout=subprocess.PIPE,
                                                 stderr=subprocess.PIPE)
                    mkfs_output, mkfs_error = mkfs_proc.communicate()
                    if mkfs_proc.returncode != 0:
                        raise Exception("Error reformatting partition to set hfs* volume label (LABEL). {}".
                                        format(target, mkfs_error))
                    if get_partition_table_type(target) == "gpt":
                        sgdisk_proc = subprocess.Popen("sgdisk -c {}:{} {}".format(partition, label, target),
                                                       stdout=subprocess.PIPE,
                                                       stderr=subprocess.PIPE,
                                                       shell=True)
                        sgdisk_output, sgdisk_error = sgdisk_proc.communicate()
                        if sgdisk_proc.returncode != 0:
                            raise Exception("Error changing GPT hfs* volume label (PARTLABEL). {}".
                                            format(str(sgdisk_error, "utf-8")))
                        part_uuid = get_gpt_partuuid(source, partition)
                        partuuid_proc = subprocess.Popen(
                            ["sgdisk", "-u", "{}:{}".format(str(partition), part_uuid), target],
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE)
                        partuuid_output, partuuid_error = partuuid_proc.communicate()
                        if partuuid_proc.returncode != 0:
                            raise Exception("Could not set PARTUUID on target device ({}{}) {}".
                                            format(target, partition, partuuid_error))
                else:
                    raise Exception("EZDuplicator does not support changing the volume label on {} filesystem.")
    except Exception as ex:
        logging.error("{} (target = {})".format(ex, target))


def partclone(source, target, pipe_connection, failed_drives):
    try:
        if EZDuplicator.lib.EZDuplicator.is_blkdev_still_valid(target):
            source_device_manager = EZDuplicator.lib.weresync.daemon.device.DeviceManager(source)
            for partition in source_device_manager.get_partitions():
                filesystem = source_device_manager.get_partition_file_system(partition)
                if filesystem in SUPPORTED_FILESYSTEM_TYPES:
                    args = ["partclone." + filesystem, "-C", "-q", "-b", "-O", target + str(partition), "-s",
                            source + str(partition)]
                    partclone_proc = subprocess.Popen(
                        args,
                        stdout=subprocess.PIPE,
                        stdin=subprocess.PIPE,
                        stderr=subprocess.PIPE)
                    output, error = partclone_proc.communicate()
                    exit_code = partclone_proc.returncode
                    if exit_code != 0:
                        raise Exception("Non-zero exit code: {}".format(str(error, "utf-8")))
            pipe_connection.send("Bump")
        else:
            logging.warning("{} is no longer a valid block device. Prematurely completing task.".format(target))
            if target not in failed_drives:
                failed_drives.append(target)
            """ We need to increase the percentage otherwise it will never reach to 100% """
            pipe_connection.send("Bump")
    except Exception as ex:
        logging.error(ex)
        if target not in failed_drives:
            failed_drives.append(target)
        """ We need to increase the percentage otherwise it will never reach to 100% """
        pipe_connection.send("Bump")


def fsck(target):
    try:
        device_manager = EZDuplicator.lib.weresync.daemon.device.DeviceManager(target)
        for partition in device_manager.get_partitions():
            filesystem = device_manager.get_partition_file_system(partition)
            if filesystem in SUPPORTED_FILESYSTEM_TYPES or filesystem == "ntfs":
                args = []
                if filesystem != "ntfs":
                    args.append("fsck." + filesystem)
                    if "fat" in filesystem or filesystem == "msdos":
                        args.append("-a")
                    elif "ext" in filesystem:
                        args.append("-p")
                    elif filesystem == "fsf2":
                        args.append("-a")
                        args.append("-f")
                        args.append("-y")
                    elif "hfs" in filesystem:
                        args.append("-f")
                        args.append("-y")
                    elif "jfs" in filesystem or filesystem == "minix":
                        args.append("-a")
                        args.append("-f")
                    elif filesystem == "reiser4":
                        args.append("-a")
                        args.append("-f")
                        args.append("-p")
                    elif filesystem == "reiserfs":
                        args.append("-a")
                        args.append("-f")
                        args.append("-y")
                    args.append(target + str(partition))
                else:
                    args = ["ntfsfix", "-b", "-d", target + str(partition)]
                logging.debug("args = {}".format(args))
                fsck_proc = subprocess.Popen(
                    args,
                    stdout=subprocess.PIPE,
                    stdin=subprocess.PIPE,
                    stderr=subprocess.PIPE)
                output, error = fsck_proc.communicate()
                exit_code = fsck_proc.returncode
                if exit_code != 0:
                    raise Exception("Non-zero exit code: {}".format(str(error, "utf-8")))
    except Exception as ex:
        logging.error(ex)


def unmount_all_partitions(target):
    if EZDuplicator.lib.EZDuplicator.is_blkdev_still_valid(target):
        target_device_manager = EZDuplicator.lib.weresync.daemon.device.DeviceManager(target)
        for partition in target_device_manager.get_partitions():
            logging.debug("Checking {} for mounted partitions...".format(target))
            try:
                while target_device_manager.mount_point(partition) is not None:
                    logging.info("Unmounting {}{}".format(target, partition))
                    target_device_manager.unmount_partition(partition)
            except EZDuplicator.lib.weresync.exception.DeviceError as ex:
                logging.warning(ex)
    else:
        logging.error("{} is no longer a valid target!".format(target))


def unmount(target):
    umount = subprocess.Popen(["umount", target], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    output, error = umount.communicate()
    if umount.returncode != 0:
        logging.warning("Could not execute umount(8)? Non-zero exit code: {}".format(str(error, "utf-8")))
        logging.warning("Need to implement lsof PID kill method!")


def clean_mount_map():
    original_map = EZDuplicator.lib.DataOnlyDuplication.get_original_mount_map()
    questionable_map = json.loads(EZDuplicator.lib.DataOnlyDuplication.get_mount2json())

    for questionable_point in questionable_map:
        if not is_in_here("on", questionable_point['on'], "device", questionable_point['device'], original_map):
            logging.info("{} on {} is not in the original mount map".format(questionable_point['device'],
                                                                            questionable_point['on']))
            unmount(questionable_point['device'])


def is_in_here(key_one, value_one, key_two, value_two, map):
    for item in map:
        if item[key_one] == value_one and item[key_two] == value_two:
            return True
    return False


def get_original_mount_map():
    with open(EZDuplicator.lib.EZDuplicator.__mounts_map__, "r") as json_file:
        data = json.load(json_file)
    return data


def get_mount2json():
    mount = subprocess.Popen(["mount"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    output, error = mount.communicate()

    if mount.returncode != 0:
        raise Exception("Could not execute mount(8)? Non-zero exit code: {}".format(str(error, "utf-8")))

    output = str(output, "utf-8")
    output_list = []
    for row in output.splitlines():
        this_row = row.split(" ")
        mount_point_dic = {"device": this_row[0], "on": this_row[2], "type": this_row[4], "flags": this_row[5]}
        output_list.append(mount_point_dic)

    """ Serialization """
    json_output = json.dumps(output_list, indent=4)
    return json_output


def grep_mount(what, explicit=False):
    if explicit:
        grep = subprocess.Popen("mount | grep -w '{}'".format(what),
                                stderr=subprocess.PIPE, stdout=subprocess.PIPE, shell=True)
    else:
        grep = subprocess.Popen("mount | grep '{}'".format(what),
                                stderr=subprocess.PIPE, stdout=subprocess.PIPE, shell=True)
    output, error = grep.communicate()

    if grep.returncode >= 2:
        raise Exception("Error while grepping mount(8) Non-zero exit code: {}".format(str(error, "utf-8")))

    if len(output) > 0:
        return True
    else:
        return False


def mount_all_source_partitions(source):
    EZDuplicator.lib.EZDuplicator.mkdir("/tmp/mnt")
    EZDuplicator.lib.EZDuplicator.mkdir("/tmp/mnt/source")
    """ Do not use tempfile.TemporaryDirectory() as it will delete data inside of target and source! """
    device_manager = EZDuplicator.lib.weresync.daemon.device.DeviceManager(source)
    for partition in device_manager.get_partitions():
        filesystem = device_manager.get_partition_file_system(partition)
        if filesystem is not None and filesystem != "swap" and filesystem in SUPPORTED_FILESYSTEM_TYPES:
            if device_manager.mount_point(partition) is None:
                prefix = source.split("/")[2] + str(partition) + "_"
                temp_source = tempfile.mkdtemp(dir="/tmp/mnt/source", prefix=prefix)
                try:
                    device_manager.mount_partition(partition, temp_source)
                except EZDuplicator.lib.weresync.exception.DeviceError as ex:
                    logging.warning(ex)


def data_only_duplication(source, target, pipe_connection, failed_drives):
    """ Setup temporary directories to mount source and target. These need to be deleted manually."""
    EZDuplicator.lib.EZDuplicator.mkdir("/tmp/mnt")
    EZDuplicator.lib.EZDuplicator.mkdir("/tmp/mnt/source")
    EZDuplicator.lib.EZDuplicator.mkdir("/tmp/mnt/target")
    source_prefix = source.split("/")[2] + "_"
    target_prefix = target.split("/")[2] + "_"
    """ Do not use tempfile.TemporaryDirectory() as it will delete data inside of target and source! """
    temp_source = tempfile.mkdtemp(dir="/tmp/mnt/source", prefix=source_prefix)
    temp_target = tempfile.mkdtemp(dir="/tmp/mnt/target", prefix=target_prefix)

    try:
        if EZDuplicator.lib.EZDuplicator.is_blkdev_still_valid(target):
            """ Determine the source type of partition table. EZDuplicator only supports (ms)dos/MBR and GPT at the 
            moment """
            partition_table = get_partition_table_type(source)

            """ Null the partition table on target """
            logging.debug("set_partition_table_null({})".format(target))
            set_partition_table_null(target)

            """ Recreate a new blank partition table on the target """
            logging.debug("set_partition_table({}, {})".format(target, partition_table))
            set_partition_table(target, partition_table)

            """ Copy the partition table from source to target """
            device_copier = EZDuplicator.lib.weresync.daemon.device.DeviceCopier(
                source, target, temp_source, temp_target)
            logging.debug("transfer_partition_table({} -> {})".format(source, target))
            device_copier.transfer_partition_table(resize=False)

            """ Validate the partition table """
            logging.info("Validating partition table on {}".format(target))
            device_copier.partitions_valid()
            sleep(.2)

            """ Copy UUID & PARTUUID from the source to targets """
            logging.info("copy_partuuids({}, {})".format(source, target))
            copy_partuuids(source, target)
            logging.info("copy_uuids({}, {})".format(source, target))
            copy_uuids(source, target)
            logging.info("copy_labels({}, {})".format(source, target))
            copy_labels(source, target)

            # logging.info("partclone({}, {})".format(source, target))
            # partclone(source, target)

            # print("data_only_duplication() print(glob.glob(/dev/sda*) = {}".format(glob.glob("/dev/sda*")))
            """ Finally, copy each file from each partition from the source to the target """
            # print("data_only_duplication() device_copier.copy_files({}, {}, excluded_partitions={})".
            #      format(temp_source, temp_target, excluded_partitions))
            # device_copier.copy_files(temp_source, temp_target, excluded_partitions=excluded_partitions)

            pipe_connection.send("Bump")
        else:
            logging.warning("{} is no longer a valid block device. Prematurely completing task.".format(target))
            failed_drives.append(target)
            """ We need to increase the percentage otherwise it will never reach to 100% """
            pipe_connection.send("Bump")
    except (OSError, IOError, Exception, EOFError, SystemError, RuntimeError,
            EZDuplicator.lib.weresync.exception.CopyError, EZDuplicator.lib.weresync.exception.DeviceError,
            EZDuplicator.lib.weresync.exception.InvalidVersionError,
            EZDuplicator.lib.weresync.exception.PluginNotFoundError,
            EZDuplicator.lib.weresync.exception.UnsupportedDeviceError) as ex:

        logging.error("{}: {}".format(target, ex), exc_info=sys.exc_info())
        if target not in failed_drives:
            failed_drives.append(target)

        """ Allow the progress bar to reach 100% even when exceptions occur """
        pipe_connection.send("Bump")


def is_in_list(element, xxhsum_list):
    for row in xxhsum_list:
        for column in row:
            if column == element:
                return True
    return False


def cleanup_dirs():
    source_dirs = [source_dirs for source_dirs in Path("/tmp/mnt/source").glob("**/*") if source_dirs.is_dir()]
    target_dirs = [target_dirs for target_dirs in Path("/tmp/mnt/target").glob("**/*") if target_dirs.is_dir()]
    try:
        if len(source_dirs) > 0:
            for directory in source_dirs:
                os.rmdir(directory)
        if len(target_dirs) > 0:
            for directory in target_dirs:
                os.rmdir(directory)
    except Exception as ex:
        logging.error(ex)


def data_only_qa(target, pipe_connection, list_of_failed_drives, list_of_source_xxhsums):
    try:
        if EZDuplicator.lib.EZDuplicator.is_blkdev_still_valid(target):
            logging.info("{} is no longer a valid block device?".format(target))
            """ if target not in list_of_failed_drives:
                list_of_failed_drives.append(target) """
            """ Increase the percentage complete otherwise it will never reach to 100% """
            """ pipe_connection.send("Bump") """

        if target not in list_of_failed_drives:
            list_of_target_xxhsums = get_list_of_xxhsums(target, list_of_failed_drives)
            if target not in list_of_failed_drives:
                """ Compare the checksums from the target to those of the source """
                for row in list_of_target_xxhsums:
                    for checksum in row:
                        if not is_in_list(checksum, list_of_source_xxhsums):
                            logging.error("{} is not in list of source xxhsums!".format(checksum))
                            if target not in list_of_failed_drives:
                                list_of_failed_drives.append(target)
                """ Compare the checksums from the source to those of the target """
                for row in list_of_source_xxhsums:
                    for checksum in row:
                        if not is_in_list(checksum, list_of_target_xxhsums):
                            logging.error("{} from {} is not in list of source xxhsums!".format(checksum, target))
                            if target not in list_of_failed_drives:
                                list_of_failed_drives.append(target)
                pipe_connection.send("Bump")
            else:
                logging.info(
                    "No need to get xxhsum hash for {}, failed to aquire xxhsums.".format(target))
                pipe_connection.send("Bump")
        else:
            logging.info("No need to get xxhsum hash for {}, already failed duplication process.".format(target))
            pipe_connection.send("Bump")
    except (OSError, IOError, Exception, EOFError, SystemError, RuntimeError) as ex:
        logging.error(ex)
        if target not in list_of_failed_drives:
            list_of_failed_drives.append(target)

        """ Allow the progress bar to reach 100% even when exceptions occur """
        pipe_connection.send("Bump")


def get_size_of_used_space(target):
    try:
        device_manager = EZDuplicator.lib.weresync.daemon.device.DeviceManager(target)
        partitions = device_manager.get_partitions()
        size_of_target_onek = 0

        for partition in partitions:
            size_of_target_onek += device_manager.get_partition_used(partition)

        return size_of_target_onek * 1000

    except Exception as ex:
        logging.error(ex)
        return 0


def get_human_size(bites, decimal_place=2):
    for unit in ['B', 'KB', 'MB', 'GB', 'TB', 'PB']:
        if bites < 1000.00 or unit == 'PB':
            break
        bites /= 1000.0
    return f"{bites:.{decimal_place}f} {unit}"


def get_list_of_xxhsums(target, failed_drives):
    try:
        device_manager = EZDuplicator.lib.weresync.daemon.device.DeviceManager(target)
        partitions = device_manager.get_partitions()
        rows = []
        columns = []

        """ Unmount all partitions of the target """
        unmount_all_partitions(target)

        for i in range(len(partitions)):
            """ Get xxhsums for each file in each partition """
            logging.debug("Acquiring xxhsums for {}{}".format(target, partitions[i]))
            try:
                partition_file_system = device_manager.get_partition_file_system(partitions[i])
                if partition_file_system is not None and partition_file_system != "swap":
                    if device_manager.mount_point(partitions[i]) is None:
                        target_prefix = target.split("/")[2] + str(partitions[i]) + "_"
                        temp_target = tempfile.mkdtemp(dir="/tmp/mnt/target", prefix=target_prefix)
                        device_manager.mount_partition(partitions[i], temp_target)
                    else:
                        temp_target = device_manager.mount_point(partitions[i])
                    files = [file for file in Path(temp_target).glob("**/*")
                             if file.is_file() and 'System Volume Information' not in str(os.path.abspath(file))]
                    for j in range(len(files)):
                        checksum = EZDuplicator.lib.EZDuplicator.get_xxhsum_hash(
                            os.path.abspath(str(files[j])), failed_drives)
                        columns.append(checksum)
                    rows.append(columns)
                    columns = []
                else:
                    logging.info("File system on {}{} is not supported ({})".format(target, str(partitions[i]),
                                                                                    partition_file_system))
            except Exception as ex:
                logging.error("Error while trying to acquire xxhsum on {}{}: {}".format(target, partitions[i], ex))
                if target not in failed_drives:
                    failed_drives.append(target)
        logging.debug("Finished acquiring all xxhsums for {}".format(target))
        return rows
    except Exception as ex:
        logging.error(ex)
        if target not in failed_drives:
            failed_drives.append(target)
