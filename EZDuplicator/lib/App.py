"""

Copyright (c) 2021 Connor McMillan <connor@mcmillan.website>. All rights reserved.

This work is licensed under the terms of the MIT license.
For a copy, see <https://opensource.org/licenses/MIT>.

"""
import glob
import logging
import os
import subprocess
import time
from pathlib import Path

import serial
from gi import require_version as gi_require_version

import EZDuplicator.AppCrashedDialog
import EZDuplicator.lib.EZDuplicator
import EZDuplicator.lib.webtail

gi_require_version('Gtk', '3.0')


def webtail_http_server_daemon():
    filename = EZDuplicator.lib.EZDuplicator.__dot_log_file__
    port = EZDuplicator.lib.EZDuplicator.__webtail_http_server_port__
    if filename is None:
        logging.error('No input file to tail')
        return
    try:
        EZDuplicator.lib.webtail.WebTailHTTPRequestHandler.filename = filename
        server_address = ('', int(port))
        httpd = EZDuplicator.lib.webtail.WebTailServer(server_address,
                                                       EZDuplicator.lib.webtail.WebTailHTTPRequestHandler)
        logging.info('Starting HTTP webtail server at port %d', server_address[1])
        httpd.serve_forever()
    except KeyboardInterrupt:
        logging.info('HTTP server stopped')


def update_date_and_time_daemon(pipe_connection):
    while True:
        pipe_connection.send("{}\n{}".format(time.strftime('%I:%M:%S %p'), time.strftime('%m/%d/%y')))
        time.sleep(1)


def update_number_of_usbs_daemon(pipe_connection):
    source_bypath = EZDuplicator.lib.EZDuplicator.get_config_setting('source_dev_path')
    while True:
        number_of_usbs = EZDuplicator.lib.EZDuplicator.get_number_or_list_of_usbs(
            'number', source_bypath, debug=False, warnings=True)
        pipe_connection.send(number_of_usbs)


def get_com_port():
    try:
        com_port = serial.Serial()
        com_port.port = EZDuplicator.lib.EZDuplicator.get_config_setting("twelve_v_com_port")
        com_port.baudrate = 115200
        com_port.bytesize = serial.EIGHTBITS  # number of bits per bytes
        com_port.parity = serial.PARITY_NONE  # set parity check: no parity
        com_port.stopbits = serial.STOPBITS_ONE  # number of stop bits
        com_port.timeout = 1  # non-block read
        com_port.xonxoff = False  # disable software flow control
        com_port.rtscts = False  # disable hardware (RTS/CTS) flow control
        com_port.dsrdtr = True  # disable hardware (DSR/DTR) flow control
        com_port.writeTimeout = 2  # timeout for write
        return com_port
    except Exception as ex:
        logging.error(ex)


def heartbeat_watchdog_daemon(conn):
    has_usb_pci_controller_issue = False
    resuscitation_attempts = 0

    update_twelve_vpm()

    while resuscitation_attempts <= 5:
        com_port = get_com_port()

        try:
            com_port.open()
        except Exception as ex:
            logging.error(ex)

        if com_port.isOpen():
            try:
                missed_acks = 0
                com_port.flushInput()
                com_port.flushOutput()

                while True:
                    com_port.write("HEARTBEAT".encode())
                    time.sleep(1)
                    rsp = com_port.readline().decode()
                    if rsp == "":
                        missed_acks += 1
                        if missed_acks > 1:
                            logging.error("Missed ACK packet! (#{})".format(missed_acks))
                        if missed_acks >= 3:
                            resuscitation_attempts += 1
                            break
                    try:
                        if not has_usb_pci_controller_issue:
                            number_of_usb_hubs = \
                                int(EZDuplicator.lib.EZDuplicator.get_config_setting('number_of_usb_hubs'))
                            expected_number_of_controllers = (((number_of_usb_hubs - 1) * 2) + number_of_usb_hubs)
                            actual_number_of_controllers = \
                                EZDuplicator.lib.EZDuplicator.get_number_of_usb_pci_controllers()
                            if expected_number_of_controllers != actual_number_of_controllers:
                                logging.error("The number of USB/PCI controllers visible ({}) does not equal the "
                                              "expected number of controllers that the OS should see! ({})".
                                              format(actual_number_of_controllers, expected_number_of_controllers))
                                logging.error("Asking operator to powercycle EZDuplicator!")
                                conn.send("Exception")
                                has_usb_pci_controller_issue = True
                    except Exception as ex:
                        logging.error(ex)
            except Exception as ex:
                resuscitation_attempts += 1
                com_port.close()
                logging.error(ex)
        else:
            resuscitation_attempts += 1
            logging.error("{} is not open?".format(com_port.port))
            com_port = get_com_port()

            try:
                com_port.open()
            except Exception as ex:
                logging.error(ex)

    """ At last, notify operator that we can't resuscitate the 12VPM """
    logging.error("Ran out of resuscitation attempts!")
    conn.send("Exception")


def update_twelve_vpm():
    com_port = get_com_port()

    """ Update 12VPM firmware? """
    """ Grab a list of available firmware updates for the 12V Power Manager """
    i = 0
    grep = EZDuplicator.lib.EZDuplicator.__vpm_dir__ + "*.hex"
    hex_file = ""
    full_hex_file = ""
    for firmware in glob.glob(grep):
        """ os.path.basename("../12VPM/100.hex") = 100.hex """
        hex_file = os.path.basename(firmware)
        full_hex_file = firmware
        logging.info("Hex file found: {}".format(firmware))
        i += 1

    """ There should never be more than one unflashed hex file """
    if i > 1:
        logging.info("Not updating 12VPM firmware. More than one unflashed file found!")
    elif i == 0:
        logging.info("No flashable firmware found.")
    else:
        try:
            com_port.open()
        except Exception as ex:
            logging.error("Trying to update 12VPM firmware but: {}".format(ex))
            EZDuplicator.AppCrashedDialog.AppCrashedDialog()
            exit()
        if com_port.isOpen():
            try:
                missed_acks = 0
                com_port.flushInput()
                com_port.flushOutput()

                installed = ""
                for i in range(4):
                    com_port.write("VERSION".encode())
                    time.sleep(1)
                    installed = com_port.readline().decode()
                    if installed == "":
                        missed_acks += 1
                        if missed_acks > 1:
                            logging.warning("12VPM did not respond with version info! (#{})".format(missed_acks))
                com_port.close()

                available = Path(hex_file).with_suffix('').__str__()
                if installed != "" and int(installed) < int(available):
                    logging.info("Updating firmware to v{} using {}".format(available, full_hex_file))

                    EZDuplicator.lib.EZDuplicator.mkdir(EZDuplicator.lib.EZDuplicator.__log_dir__)
                    log_file = open(EZDuplicator.lib.EZDuplicator.__log_dir__ + "{}.log".format(hex_file), 'a+')
                    output = \
                        subprocess.Popen("avrdude -v -p atmega328p -c arduino -P {} -b 115200 -D -U flash:w:{}:i".
                                         format(EZDuplicator.lib.EZDuplicator.get_config_setting("twelve_v_com_port"),
                                                full_hex_file),
                                         stdout=log_file, stderr=log_file, shell=True)
                    output.communicate()

                    successful = False
                    with open(EZDuplicator.lib.EZDuplicator.__log_dir__ + "{}.log".format(hex_file)) as line:
                        if "bytes of flash verified" in line.read():
                            successful = True
                            logging.info("Firmware update successful! ({})".format(hex_file))
                            """ Rename recently flashed firmware to something 'current' to evade update loops. """
                            os.rename("{}".format(full_hex_file), "{}.flashed".format(full_hex_file))

                    if not successful:
                        logging.error("Firmware update was NOT successful?! ({})".format(hex_file))
                        """ Should we do some more stuff here? Like rename the the unsuccessful firmware file? """
                else:
                    os.rename("{}".format(full_hex_file), "{}.skipped".format(full_hex_file))
                    logging.info("No need to update firmware, available={} installed={}".
                                 format(available, installed))
            except Exception as ex:
                logging.error("Firmware update failed: {}".format(ex))
                if "device reports rediness" in ex:
                    update_twelve_vpm()
