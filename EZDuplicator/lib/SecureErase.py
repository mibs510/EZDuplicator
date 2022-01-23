"""

Copyright (c) 2021 Connor McMillan <connor@mcmillan.website>. All rights reserved.

This work is licensed under the terms of the MIT license.
For a copy, see <https://opensource.org/licenses/MIT>.

"""
import logging
import multiprocessing
import queue
import random
import sys
from multiprocessing import Process, Queue, current_process

import EZDuplicator.lib.EZDuplicator


def secure_erase_process(pipe_connection, pids, failed_drives):
    logging.info("================== Begin Secure Earse ==================")
    source_by_path = EZDuplicator.lib.EZDuplicator.get_source_by_path()
    targets = EZDuplicator.lib.EZDuplicator.get_number_or_list_of_usbs('list', source_by_path)
    number_of_targets = EZDuplicator.lib.EZDuplicator.get_number_or_list_of_usbs('number', source_by_path)
    processes = []
    number_of_processes = multiprocessing.cpu_count()
    tasks_to_accomplish = Queue()
    tasks_that_are_done = Queue()

    """ Pass 1 """
    for usb in targets:
        logging.info("Begin Pass 1 on {}".format(usb))
        tasks_to_accomplish.put(usb)

    # creating processes
    for w in range(number_of_processes):
        process = Process(target=pass_,
                          args=(tasks_to_accomplish, tasks_that_are_done, pipe_connection, 1, failed_drives),
                          daemon=True)
        processes.append(process)
        process.start()
        pids.append(process.pid)

    # completing process
    for process in processes:
        process.join()

    while not tasks_that_are_done.empty():
        logging.info(tasks_that_are_done.get())

    tasks_that_are_done.close()
    tasks_to_accomplish.close()

    """ Pass 2 """
    tasks_to_accomplish = Queue()
    tasks_that_are_done = Queue()

    for usb in targets:
        logging.info("Begin Pass 2 on {}".format(usb))
        tasks_to_accomplish.put(usb)

    # creating processes
    for w in range(number_of_processes):
        process = Process(target=pass_,
                          args=(tasks_to_accomplish, tasks_that_are_done, pipe_connection, 2, failed_drives),
                          daemon=True)
        processes.append(process)
        process.start()
        pids.append(process.pid)

    # completing process
    for process in processes:
        process.join()

    while not tasks_that_are_done.empty():
        logging.info(tasks_that_are_done.get())

    tasks_that_are_done.close()
    tasks_to_accomplish.close()

    """ Pass 3 """
    tasks_to_accomplish = Queue()
    tasks_that_are_done = Queue()

    for usb in targets:
        logging.info("Begin Pass 3 on {}".format(usb))
        tasks_to_accomplish.put(usb)

    # creating processes
    for w in range(number_of_processes):
        process = Process(target=pass_,
                          args=(tasks_to_accomplish, tasks_that_are_done, pipe_connection, 3, failed_drives),
                          daemon=True)
        processes.append(process)
        process.start()
        pids.append(process.pid)

    # completing process
    for process in processes:
        process.join()

    while not tasks_that_are_done.empty():
        logging.info(tasks_that_are_done.get())

    tasks_that_are_done.close()
    tasks_to_accomplish.close()

    pipe_connection.send("Finished")

    if len(failed_drives) == 0:
        EZDuplicator.lib.EZDuplicator.send_email_notification(
            "Secure Erase", "{} drive(s) securely erased".format(number_of_targets), "Successful", test=False)
    elif len(failed_drives) > 0:
        logging.debug("number_of_failed_drives = {}, failed_drives = {}".format(len(failed_drives), failed_drives))
        pipe_connection.send("Enable_QADialog_Button")
        EZDuplicator.lib.EZDuplicator.send_email_notification(
            "Secure Erase", "{}/{} drive(s) failed to securely erase".format(
                len(failed_drives), number_of_targets), "Unsuccessful", test=False)

    logging.info("================== End Secure Erase ==================")


def cancel(number_of_usbs, pids, cancel_io_watch):
    try:
        cancel_io_watch.send("spinner")
        cancel_io_watch.send("terminate")
        EZDuplicator.lib.EZDuplicator.kill_pids(pids)
        EZDuplicator.lib.EZDuplicator.send_email_notification(
            "Secure Erase", "Operator aborted {} drive(s) while securely erasing".format(
                number_of_usbs), "Incomplete", test=False)
        cancel_io_watch.send("destroy")
    except Exception as ex:
        logging.error(ex, exc_info=sys.exc_info())


def stop(pids, stop_io_watch):
    try:
        stop_io_watch.send("spinner")
        stop_io_watch.send("terminate")
        EZDuplicator.lib.EZDuplicator.kill_pids(pids)
        EZDuplicator.lib.EZDuplicator.send_email_notification("Secure Erase",
                                                              "Review debug console for further details.",
                                                              "Fatal Error Occured", test=False)
        stop_io_watch.send("stop")
    except Exception as ex:
        logging.error(ex, exc_info=sys.exc_info())


def over_write(target, integer, pipe_connection, failed_drives):
    try:
        if EZDuplicator.lib.EZDuplicator.is_blkdev_still_valid(target):
            with open(target, 'wb+') as usb:
                for i in range(0, EZDuplicator.lib.EZDuplicator.get_size_in_bytes(target)):
                    usb.write(integer.to_bytes(1, 'big'))
            pipe_connection.send("Bump")
        else:
            logging.info("{} is no longer a valid block device.".format(target))
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


def pass_(tasks_to_accomplish, tasks_that_are_done, pipe_connection, pass_number, failed_drives):
    while True:
        try:
            '''
                try to get task from the queue. get_nowait() function will 
                raise queue.Empty exception if the queue is empty. 
                queue(False) function would do the same task also.
            '''
            task = tasks_to_accomplish.get_nowait()
            if pass_number == 1:
                logging.info("over_write({}, 0)".format(task))
                over_write(task, 0, pipe_connection, failed_drives)
            elif pass_number == 2:
                logging.info("over_write({}, 255)".format(task))
                over_write(task, 255, pipe_connection, failed_drives)
            elif pass_number == 3:
                random_int = random.randint(0, 255)
                logging.info("over_write({}, {})".format(task, random_int))
                over_write(task, random_int, pipe_connection, failed_drives)
        except queue.Empty:

            break
        except (OSError, IOError, Exception, EOFError, SystemError, RuntimeError) as ex:
            logging.error(ex)
        else:
            '''
                if no exception has been raised, add the task completion 
                message to task_that_are_done queue
            '''
            tasks_that_are_done.put("Pass " + str(pass_number) + ": " + task + " was completed by " +
                                    current_process().name)
    return True
