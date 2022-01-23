"""

Copyright (c) 2021 Connor McMillan <connor@mcmillan.website>. All rights reserved.

This work is licensed under the terms of the MIT license.
For a copy, see <https://opensource.org/licenses/MIT>.

"""
import logging
import multiprocessing
import queue
import resource
import sys
import time
from multiprocessing import current_process, Process, Queue

import EZDuplicator.lib.EZDuplicator


def bpb_duplication_process(pipe_connection, pids, failed_drives):
    logging.info("================== Begin BPB Duplication ==================")
    source_by_path = EZDuplicator.lib.EZDuplicator.get_source_by_path()
    source = EZDuplicator.lib.EZDuplicator.get_source_blkdev(source_by_path)
    targets = EZDuplicator.lib.EZDuplicator.get_number_or_list_of_usbs('list', source_by_path)
    number_of_targets = EZDuplicator.lib.EZDuplicator.get_number_or_list_of_usbs('number', source_by_path)
    processes = []
    number_of_processes = multiprocessing.cpu_count() * 2
    tasks_to_accomplish = Queue()
    tasks_that_are_done = Queue()

    """ Duplication """
    for target in targets:
        logging.info("Begin BPB duplication on {}".format(target))
        tasks_to_accomplish.put(target)

    # creating processes
    for w in range(number_of_processes):
        process = Process(target=dupication_task_manager,
                          args=(tasks_to_accomplish, tasks_that_are_done, pipe_connection, source, failed_drives),
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

    """ Quality Check """
    if len(failed_drives) != int(number_of_targets):
        """ Get source drive hash for comparison """
        logging.info("Get xxhsum hash from source drive {}".format(source))
        source_xxhash = EZDuplicator.lib.EZDuplicator.get_xxhsum_hash(source, failed_drives)
        logging.info("xxhsum hash from source drive = {}".format(source_xxhash))
        if source in failed_drives:
            """ Did we fail to get checksum(s) from the source? """
            logging.error("Cannot proceed! Failed to obtain checksum(s) from source!")
            pipe_connection.send("Stop")
            EZDuplicator.lib.EZDuplicator.sleep_indfinite()

        pipe_connection.send("Bump")

        tasks_to_accomplish = Queue()
        tasks_that_are_done = Queue()

        for target in targets:
            logging.info("Begin QA check on {}".format(target))
            tasks_to_accomplish.put(target)

        # creating processes
        for w in range(number_of_processes):
            process = Process(target=qa_task_manager,
                              args=(tasks_to_accomplish, tasks_that_are_done, pipe_connection, source, source_xxhash,
                                    failed_drives),
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
    else:
        logging. \
            info("Skipping QA section. Number of failed drives is equal to the amount of drives to be duplicated.")
        """ Increase the progress bar because getting the xxhsum hash of the source drive is a considered 
        fractional progression"""
        pipe_connection.send("Bump")
        """ Increase the progressbar since we are skipping the QA section. """
        for i in range(int(number_of_targets)):
            pipe_connection.send("Bump")

    if len(failed_drives) == 0:
        EZDuplicator.lib.EZDuplicator.send_email_notification("Bit-Per-Bit Duplication", "{} drive(s) duplicated".
                                                              format(number_of_targets), "Successful", test=False)
    elif len(failed_drives) > 0:
        logging.debug("number_of_failed_drives = {}, failed_drives = {}".format(len(failed_drives), failed_drives))
        pipe_connection.send("Enable_QADialog_Button")
        EZDuplicator.lib.EZDuplicator.send_email_notification("Bit-Per-Bit Duplication", "{}/{} drive(s) failed".
                                                              format(len(failed_drives), number_of_targets),
                                                              "Unsuccessful", test=False)

    logging.info("================== End BPB Duplication ==================")


def cancel(number_of_usbs, pids, cancel_io_watch):
    try:
        cancel_io_watch.send("spinner")
        cancel_io_watch.send("terminate")
        EZDuplicator.lib.EZDuplicator.kill_pids(pids)
        EZDuplicator.lib.EZDuplicator.send_email_notification(
            "Bit-Per-Bit Duplication", "Operator aborted {} drive(s) during Bit-Per-Bit duplication".format(
                number_of_usbs), "Incomplete", test=False)
        cancel_io_watch.send("destroy")
    except Exception as ex:
        logging.error(ex, exc_info=sys.exc_info())


def stop(pids, stop_io_watch):
    try:
        stop_io_watch.send("spinner")
        EZDuplicator.lib.EZDuplicator.kill_pids(pids)
        stop_io_watch.send("terminate")
        EZDuplicator.lib.EZDuplicator.send_email_notification(
            "Bit-Per-Bit Duplication", "Review debug console for further details.",
            "Fatal Error Occured", test=False)
        stop_io_watch.send("stop")
    except Exception as ex:
        logging.error(ex, exc_info=sys.exc_info())


def bpb_duplication(source, target, pipe_connection, failed_drives):
    source_size = EZDuplicator.lib.EZDuplicator.get_size_in_bytes(source)
    target_size = EZDuplicator.lib.EZDuplicator.get_size_in_bytes(target)
    bytes_to_copy = 0

    if source_size > target_size:
        bytes_to_copy = target_size
        logging.info("Source is larger (bytes: {}) than target drive (bytes: {})".
                     format(source_size, target_size))
    elif source_size < target_size:
        bytes_to_copy = source_size
        logging.info("Source drive is smaller (bytes: {}) than target drive (bytes: {})".
                     format(source_size, target_size))
    elif source_size == target_size:
        bytes_to_copy = source_size

    try:
        if EZDuplicator.lib.EZDuplicator.is_blkdev_still_valid(target):
            with open(source, 'wb+') as source:
                with open(target, 'wb+') as target:
                    for i in range(0, bytes_to_copy):
                        target.write(source.read(1))
            pipe_connection.send("Bump")
            logging.info("Task completed ({})".format(target))
        else:
            logging.info("{} is no longer a valid block device. Prematurely completing task.".format(target))
            failed_drives.append(target)
            """ We need to increase the percentage otherwise it will never reach to 100% """
            pipe_connection.send("Bump")
    except (OSError, IOError, Exception, EOFError, SystemError, RuntimeError) as ex:
        logging.error("Exception with target.write(). Prematurely completing task for {}. Exception details: {}".
                      format(target, ex))
        failed_drives.append(target)
        """ Allow the progress bar to reach 100% even when exceptions occur """
        pipe_connection.send("Bump")


def bpb_qa(target, pipe_connection, source_xxhash, failed_drives):
    try:
        if EZDuplicator.lib.EZDuplicator.is_blkdev_still_valid(target):
            if target not in failed_drives:
                target_xxhash = EZDuplicator.lib.EZDuplicator.get_xxhsum_hash(target, failed_drives)
                if target_xxhash != source_xxhash:
                    logging.info("{} xxhsum hash ({}) does not match source xxhsum hash! ({})".
                                 format(target, target_xxhash, source_xxhash))
                    failed_drives.append(target)
                pipe_connection.send("Bump")
                logging.info("Task completed ({})".format(target))
            else:
                logging.info("No need to get xxhsum hash for {}, already failed duplication process.".format(target))
                pipe_connection.send("Bump")
        else:
            logging.info("{} is no longer a valid block device. Prematurely completing task.".format(target))
            if target not in failed_drives:
                failed_drives.append(target)
            """ We need to increase the percentage otherwise it will never reach to 100% """
            pipe_connection.send("Bump")
    except (OSError, IOError, Exception, EOFError, SystemError, RuntimeError) as ex:
        logging.error(ex)
        if target not in failed_drives:
            failed_drives.append(target)

        """ Allow the progress bar to reach 100% even when exceptions occur """
        pipe_connection.send("Bump")


def dupication_task_manager(tasks_to_accomplish, tasks_that_are_done, pipe_connection, source, failed_drives):
    while True:
        try:
            '''
                try to get task from the queue. get_nowait() function will 
                raise queue.Empty exception if the queue is empty. 
                queue(False) function would do the same task also.
            '''
            task = tasks_to_accomplish.get_nowait()
            logging.info("bpb_duplication({} -> {})".format(source, task))
            """ It has been observed that low quality USB drives will lock the open.write() method.
            In doing so, it causes a memory leak/runoff until the kernel OOM (out_of_memory) decides to terminate the 
            process. This will cease the taskManager() method from putting the task in the tasks acommplished Queue.
            Py Gtk never receives signals that progress has been made and therefore the progressbar never reachs 100%. 
            TODO/WIP: Add a feature to alert operator of failed USB drives that is mapped physically by row and column
            so that appropiate actions may be taken. """
            soft, hard = resource.getrlimit(resource.RLIMIT_AS)
            """ Limit process to 256MB of RAM """
            resource.setrlimit(resource.RLIMIT_AS, (268435456, hard))

            bpb_duplication(source, task, pipe_connection, failed_drives)
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


def qa_task_manager(tasks_to_accomplish, tasks_that_are_done, pipe_connection, source, source_xxhash, failed_drives):
    while True:
        try:
            '''
                try to get task from the queue. get_nowait() function will 
                raise queue.Empty exception if the queue is empty. 
                queue(False) function would do the same task also.
            '''
            task = tasks_to_accomplish.get_nowait()
            logging.info("bpb_qa({} =? {})".format(source, task))
            """ It has been observed that low quality USB drives will lock the open.write() method.
            In doing so, it causes a memory leak/runoff until the kernel OOM (out_of_memory) decides to terminate the 
            process. This will cease the taskManager() method from putting the task in the tasks acommplished Queue.
            Py Gtk never receives signals that progress has been made and therefore the progressbar never reachs 100%. 
            TODO/WIP: Add a feature to alert operator of failed USB drives that is mapped physically by row and column
            so that appropiate actions may be taken. """
            soft, hard = resource.getrlimit(resource.RLIMIT_AS)
            """ Limit process to 256MB of RAM """
            resource.setrlimit(resource.RLIMIT_AS, (268435456, hard))

            bpb_qa(task, pipe_connection, source_xxhash, failed_drives)
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
