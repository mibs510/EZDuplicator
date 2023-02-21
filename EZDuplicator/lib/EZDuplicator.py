"""

Copyright (c) 2021 Connor McMillan <connor@mcmillan.website>. All rights reserved.

This work is licensed under the terms of the MIT license.
For a copy, see <https://opensource.org/licenses/MIT>.

"""
import configparser
import http.client
import json
import logging
import os
import pathlib
import pwd
import re
import signal
import smtplib
import socket
import ssl
import subprocess
import sys
import time
from email.mime.text import MIMEText
from logging.handlers import RotatingFileHandler
from string import ascii_lowercase

import psutil
import requests
import sentry_sdk
import xxhash
from pythonjsonlogger import jsonlogger

import EZDuplicator.WTHDialog

""" Global Variables """
__etc_dir__ = "/etc/EZDuplicator/"
__usr_dir__ = "/usr/local/lib/python3.9/dist-packages/EZDuplicator"
__root_dir__ = str(pathlib.Path(str(pathlib.Path(__file__).parent.absolute())).parent.absolute())
__log_dir__ = "/var/log/EZDuplicator/"
__vpm_dir__ = __root_dir__ + "/12VPM/"

__config_file__ = __etc_dir__ + "config.ini"
__ports_map__ = __etc_dir__ + "ports_map.json"
__mounts_map__ = __etc_dir__ + "mounts_map.json"
__dot_log_file__ = __log_dir__ + "EZDApp.log"
__json_log_file__ = __log_dir__ + "EZDApp.json"

__webtail_http_server_port__ = 3565

__splash_animation__ = __usr_dir__ + "/res/Intro_Light.mp4"

class GracefulKiller:
    kill_now = False

    def __init__(self):
        signal.signal(signal.SIGINT, self.exit_gracefully)
        signal.signal(signal.SIGTERM, self.exit_gracefully)

    def exit_gracefully(self, *args):
        self.kill_now = True


def get_absolute_file_path(python_file, assest_file):
    return str(pathlib.Path(python_file).parent.absolute()) + assest_file


def sleep_indfinite():
    while True:
        time.sleep(1)


def kill_pids(pids):
    try:
        """ Terminate all sub-process called by verification_process() """
        for pid in pids:
            if pid != 0:
                while is_alive(pid):
                    os.kill(pid, signal.SIGKILL)
                    time.sleep(0.5)
    except Exception as ex:
        logging.error(ex)


def mask_email_address(email):
    at = email.find("@")
    if at > 0:
        return email[0] + "*****" + email[at - 1:]
    else:
        return "*****@****.***"


def get_number_of_usb_pci_controllers():
    count = 0
    try:
        usb_controller_identifier = get_config_setting('usb_controller_identifier')
        pci_controller_identifier = get_config_setting('pci_controller_identifier')
        lspci = subprocess.Popen("lspci | grep \"" + usb_controller_identifier + "\" | wc -l",
                                 stderr=subprocess.PIPE,
                                 stdout=subprocess.PIPE,
                                 shell=True)
        output, error = lspci.communicate()
        exit_code = lspci.returncode
        if exit_code != 0:
            raise Exception("Non-zero exit code: {}".format(str(error, "utf-8")))
        output = str(output, "utf-8")
        try:
            count = int(output)
        except Exception as ex:
            print("Error converting {} into an integer: {}".format(output, ex))

        lspci = subprocess.Popen("lspci | grep \"" + pci_controller_identifier + "\" | wc -l",
                                 stdout=subprocess.PIPE,
                                 stderr=subprocess.PIPE,
                                 shell=True)
        output, error = lspci.communicate()
        exit_code = lspci.returncode
        if exit_code != 0:
            raise Exception("Non-zero exit code: {}".format(str(error, "utf-8")))
        output = str(output, "utf-8")
        try:
            count += int(output)
        except Exception as ex:
            print("Error converting {} into an integer: {}".format(output, ex))
        return count
    except Exception as ex:
        print("get_number_of_usb_pci_controllers(): {}".format(ex))
        return 0


def get_xxhsum_hash(target, failed_drives, blocksize=2 ** 20):
    rtn = "NULL"
    try:
        xxh = xxhash.xxh3_64()
        with open(target, "rb") as file:
            while True:
                buffer = file.read(blocksize)
                if not buffer:
                    break
                xxh.update(buffer)
            return xxh.hexdigest()
    except Exception as ex:
        logging.error(ex)
        if target not in failed_drives:
            failed_drives.append(target)
        return rtn


def get_size_in_bytes(target):
    with open(target, 'rb') as usb:
        return usb.seek(0, 2) or usb.tell()


def is_valid_port(number):
    try:
        if 1 <= int(number) <= 65535:
            return True
        else:
            raise ValueError
    except ValueError:
        return False


def is_valid_email(address):
    try:
        email_regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        if re.fullmatch(email_regex, address):
            return True
        else:
            return False
    except Exception as ex:
        logging.exception(ex)
        return False


def is_valid_hostname(hostname):
    try:
        if len(hostname) == 0:
            return False
        if hostname[-1] == ".":
            # strip exactly one dot from the right, if present
            hostname = hostname[:-1]
        if len(hostname) > 253:
            return False

        labels = hostname.split(".")

        # the TLD must be not all-numeric
        if re.match(r"[0-9]+$", labels[-1]):
            return False

        allowed = re.compile(r"(?!-)[a-z0-9-]{1,63}(?<!-)$", re.IGNORECASE)
        return all(allowed.match(label) for label in labels)
    except Exception as ex:
        logging.exception(ex)
        return False


def create_default_config(override=False):
    config = configparser.ConfigParser()
    try:
        """ Lets create a default config.ini """
        mkdir(__etc_dir__)
        if not os.path.exists(__config_file__) or override:
            if os.path.exists(__config_file__):
                os.remove(__config_file__)
            config['EZD App'] = \
                {'source_dev_path': '/dev/disk/by-path/pci-0000:00:14.0-usb-0:8:1.0-scsi-0:0:0:0',
                 'twelve_v_com_port': '/dev/serial/by-id/usb-FTDI_FT232R_USB_UART_A10K5CRG-if00-port0',
                 'number_of_usb_hubs': '8',
                 'usb_controller_identifier': 'uPD720202',
                 'pci_controller_identifier': '1812',
                 'email_enabled': 'False',
                 'rec_email_address': '',
                 'mail_host': '',
                 'mail_port': '',
                 'mail_username': '',
                 'mail_password': '',
                 'improve_software': '',
                 'syslog_enabled': 'False',
                 'syslog_host': '',
                 'syslog_port': '',
                 'update_repo': 'prod',
                 }
            with open(__config_file__, 'w') as configfile:
                config.write(configfile)
        try:
            email_enabled = get_config_setting('email_enabled')
        except Exception:
            create_default_config(override=True)
    except Exception as ex:
        logging.error(ex)


class Secrets:
    def __init__(self):
        self.oos = False
        self.ex_msg = ""
        try:
            self.secrets = \
                json.dumps(
                    requests.get("https://api.ezduplicator.com:443/get/{}/secrets".format(get_serial_number())).json())
            self.deserialized = json.loads(self.secrets)
        except Exception as ex:
            logging.exception(ex)
            """ Assume that api.ezduplicator.com/project is dead if we have trouble decoding the JSON response 
                from api.ezduplicator.com"""
            self.oos = True
            self.ex_msg = str(ex)

    def get(self, secret):
        return self.deserialized[0][secret]


def get_secret(secret):
    try:
        secrets = \
            json.dumps(
                requests.get("https://api.ezduplicator.com:443/get/{}/secrets".format(get_serial_number())).json())
        deserialized = json.loads(secrets)
        return deserialized[0][secret]
    except Exception as ex:
        logging.exception(ex)


def upload_file(file):
    try:
        upload_password = get_secret("files_password")
        data = {'upload_password': upload_password,
                'time': 'year'}
        files = {'file': open(file, 'rb')}
        download_link = requests.post("https://files.ezduplicator.com/script.php", data=data, files=files)
        return "https://files.ezduplicator.com/f.php?h={}".format(download_link.text.split('\n')[0])
    except Exception as ex:
        print(ex)


def get_serial_number():
    return subprocess.check_output("sudo dmidecode | grep 'Serial Number' | head -n1 | awk '{print $3}'",
                                   shell=True). \
        decode(encoding='ascii').strip().__str__()


def has_internet_connection():
    try:
        connection = http.client.HTTPConnection("142.250.188.14", timeout=2)
        connection.request("GET", "/")
        connection.getresponse()
        return True
    except Exception:
        return False


def get_sys_username():
    for user in psutil.users():
        if user.terminal == ":0" and user.host == "localhost":
            return user.name


def mkdir(directory):
    if not os.path.isdir(directory):
        os.mkdir(directory)
        try:
            username = get_sys_username()
            if username is not None:
                os.chown(directory, pwd.getpwnam(username).pw_uid, pwd.getpwnam(username).pw_gid)
        except Exception:
            pass


def send_cs_email_notification(serial_number, download_link):
    try:
        port = get_secret('mail_port')
        receiver_email = get_secret("cs_email")
        smtp_server = get_secret('mail_host')
        sender_email = get_secret('mail_username')
        sender_password = get_secret('mail_password')

        message = """\
<html>
<body>
An operator has sent DigitalVAR Inc. log files. Please use the following customer data to provide product support.
<br>
<br>
<b>Serial Number:</b> {serial_number}
<br>
<b>Zip File:</b> <a href="{download_link}">{download_link}</a>
<br>
<br>
This message was sent from an EZ Duplicator!
</body>
</html>""".format(serial_number=serial_number, download_link=download_link)

        email = MIMEText(message, 'html')
        email["From"] = sender_email
        email["To"] = receiver_email
        email["Subject"] = "EZD App Customer Service"

        context = ssl.create_default_context()
        with smtplib.SMTP_SSL(smtp_server, port, context=context) as server:
            """ server.set_debuglevel(1) """
            server.login(sender_email, sender_password)
            logging.info("Sending email to {}".format(receiver_email))
            server.sendmail(sender_email, receiver_email, email.as_string())
    except Exception as ex:
        logging.exception(ex)


def send_email_notification(job, msg, status, test=False):
    try:
        if get_config_setting('email_enabled') == "True" or test:
            port = get_config_setting('mail_port')
            receiver_email = get_config_setting('rec_email_address')
            smtp_server = get_config_setting('mail_host')
            sender_email = get_config_setting('mail_username')
            sender_password = get_config_setting('mail_password')
            if test:
                message = """\
From: {sender_email}
To: {receiver_email}
Subject: Test
Hello There!
    
This test message was sent from an EZ Duplicator!""".format(sender_email=sender_email, receiver_email=receiver_email)
            else:
                message = """\
From: {sender_email}
To: {receiver_email}
Subject: {job} complete!

Job: {job}
Status: {status}
Message: {msg}

This message was sent from an EZ Duplicator.""". \
                    format(sender_email=sender_email, receiver_email=receiver_email, job=job, status=status, msg=msg)

            context = ssl.create_default_context()
            with smtplib.SMTP_SSL(smtp_server, int(port), context=context) as server:
                """ server.set_debuglevel(1) """
                server.login(sender_email, sender_password)
                logging.info("Sending email to {}".format(mask_email_address(receiver_email)))
                server.sendmail(sender_email, receiver_email, message)
    except Exception as ex:
        logging.error(ex)
        if test:
            EZDuplicator.WTHDialog.WTHDialog(ex.__str__())


def improve_software():
    try:
        if get_config_setting("improve_software") == "True":
            if has_internet_connection():
                sentry_sdk.init(get_secret("dsn"))
            else:
                logging.info("We're not going to improve the software. A valid internet connection was not detected :(")
    except Exception as ex:
        logging.exception(ex)


def init_logging():
    mkdir(__log_dir__)
    logging.getLogger()
    logging.getLogger().setLevel(logging.DEBUG)

    """Catch all unhandled exceptions """
    sys.excepthook = exception_hook

    """ JSON File Handler """
    json_file_handler = RotatingFileHandler(__json_log_file__, maxBytes=10000000, backupCount=9)
    json_formatter = jsonlogger. \
        JsonFormatter("%(asctime)s %(levelname)s %(filename)s %(funcName)s %(lineno)s %(message)s",
                      datefmt="%m/%d/%y %I:%M %p")
    json_file_handler.setFormatter(json_formatter)
    logging.getLogger().addHandler(json_file_handler)

    """ .log File Handler """
    dot_log_file_handler = RotatingFileHandler(__dot_log_file__, maxBytes=10000000, backupCount=9)
    dot_log_formatter = logging.Formatter(
        "%(asctime)s %(levelname)s %(filename)s:%(funcName)s():%(lineno)s %(message)s", datefmt="[%m/%d/%y %I:%M %p]")
    dot_log_file_handler.setFormatter(dot_log_formatter)
    logging.getLogger().addHandler(dot_log_file_handler)

    """ Console Stream Handler"""
    formatter = logging.Formatter("%(asctime)s %(levelname)s %(filename)s:%(funcName)s():%(lineno)s %(message)s",
                                  datefmt="[%m/%d/%y %I:%M %p]")
    console = logging.StreamHandler()
    console.setLevel(logging.DEBUG)
    console.setFormatter(formatter)
    logging.getLogger().addHandler(console)

    """ Syslog Handler """
    if get_config_setting('syslog_enabled') == "True":
        try:
            host = get_config_setting("syslog_host")
            port = int(get_config_setting("syslog_port"))
            syslog_handler = logging.handlers.SysLogHandler(address=(host, port,),
                                                            facility=logging.handlers.SysLogHandler.LOG_DAEMON,
                                                            socktype=socket.SOCK_DGRAM)
            syslog_handler.mapPriority("INFO")
            logging.getLogger().addHandler(syslog_handler)
        except Exception as ex:
            logging.error(ex)

    """ Shhh! We don't need to expose the api to the secrets in the Debug dialog. """
    logging.getLogger("requests").setLevel(logging.WARNING)
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("parse").setLevel(logging.WARNING)


def exception_hook(type, value, traceback):
    logging.exception("Unhandled exception raised outside of try/except! Type: {}, Value: {}, Traceback: {}".
                      format(type, value, traceback), exc_info=sys.exc_info())


def get_config_setting(setting):
    try:
        config = configparser.ConfigParser()
        config.read(__config_file__)
        if config.has_option('EZD App', setting):
            return config['EZD App'][setting]
        else:
            config.set('EZD App', setting, "")
            return ""
    except Exception as ex:
        logging.exception(ex)


def set_config_setting(setting, value):
    try:
        config = configparser.ConfigParser()
        config.read(__config_file__)
        config['EZD App'][setting] = value
        with open(__config_file__, 'w') as configfile:
            config.write(configfile)
    except Exception as ex:
        logging.exception(ex)


def get_source_by_path():
    return get_config_setting("source_dev_path")


def get_number_or_list_of_usbs(number_or_list, source_by_path, absolute=True, debug=False, warnings=False):
    warning_flag = False
    number_of_drives = 0
    list_of_drives = []

    try:
        # Exclude the OS drive. This could be a serial block device (/dev/sd*).
        os_blkdev = get_os_blkdev()

        # Lets also exclude the source drive
        source_blkdev = ''
        if is_source_connected(source_by_path):
            source_blkdev = get_source_blkdev(source_by_path)

        for i in ascii_lowercase:
            """ /dev/sd* """
            if pathlib.Path("/dev/sd{}".format(i)).is_block_device():
                if is_in_lsblk_list("sd{}".format(i), absolute=False):
                    if "/dev/sd{}".format(i) != os_blkdev:
                        if "/dev/sd{}".format(i) != source_blkdev:
                            if number_or_list == 'number':
                                number_of_drives += 1
                            elif number_or_list == 'list':
                                if absolute:
                                    list_of_drives.append("/dev/sd{}".format(i))
                                else:
                                    list_of_drives.append("sd{}".format(i))
                else:
                    warning_flag = True
                    if debug:
                        logging.debug("/dev/sd{} is not in lsblk output.".format(i))

            """ /dev/sda* """
            if pathlib.Path("/dev/sda{}".format(i)).is_block_device():
                if is_in_lsblk_list("sda{}".format(i), absolute=False):
                    if "/dev/sda{}".format(i) != os_blkdev:
                        if "/dev/sda{}".format(i) != source_blkdev:
                            if number_or_list == 'number':
                                number_of_drives += 1
                            elif number_or_list == 'list':
                                if absolute:
                                    list_of_drives.append("/dev/sda{}".format(i))
                                else:
                                    list_of_drives.append("sda{}".format(i))
                else:
                    warning_flag = True
                    if debug:
                        logging.debug("/dev/sda{} is not in lsblk output.".format(i))

            """ /dev/sdb* """
            if pathlib.Path("/dev/sdb{}".format(i)).is_block_device():
                if is_in_lsblk_list("sdb{}".format(i), absolute=False):
                    if "/dev/sdb{}".format(i) != os_blkdev:
                        if "/dev/sdb{}".format(i) != source_blkdev:
                            if number_or_list == 'number':
                                number_of_drives += 1
                            elif number_or_list == 'list':
                                if absolute:
                                    list_of_drives.append("/dev/sdb{}".format(i))
                                else:
                                    list_of_drives.append("sdb{}".format(i))
                else:
                    warning_flag = True
                    if debug:
                        logging.debug("/dev/sdb{} is not in lsblk output.".format(i))

            """ /dev/sdc* """
            if pathlib.Path("/dev/sdc{}".format(i)).is_block_device():
                if is_in_lsblk_list("sdc{}".format(i), absolute=False):
                    if "/dev/sdc{}".format(i) != os_blkdev:
                        if "/dev/sdc{}".format(i) != source_blkdev:
                            if number_or_list == 'number':
                                number_of_drives += 1
                            elif number_or_list == 'list':
                                if absolute:
                                    list_of_drives.append("/dev/sdc{}".format(i))
                                else:
                                    list_of_drives.append("sdc{}".format(i))
                else:
                    warning_flag = True
                    if debug:
                        logging.debug("/dev/sdc{} is not in lsblk output.".format(i))

            """ /dev/sdd* """
            if pathlib.Path("/dev/sdd{}".format(i)).is_block_device():
                if is_in_lsblk_list("sdd{}".format(i), absolute=False):
                    if "/dev/sdd{}".format(i) != os_blkdev:
                        if "/dev/sdd{}".format(i) != source_blkdev:
                            if number_or_list == 'number':
                                number_of_drives += 1
                            elif number_or_list == 'list':
                                if absolute:
                                    list_of_drives.append("/dev/sdd{}".format(i))
                                else:
                                    list_of_drives.append("sdd{}".format(i))
                else:
                    warning_flag = True
                    if debug:
                        logging.debug("/dev/sdd{} is not in lsblk output.".format(i))

    except Exception as ex:
        logging.error(ex)
    if number_or_list == 'number':
        if warnings:
            return "{}\n{}".format(number_of_drives, warning_flag)
        else:
            return number_of_drives
    elif number_or_list == 'list':
        return list_of_drives


def get_os_blkdev():
    """
    Grab the SSD/HDD that Ubuntu is installed on to exclude it.
    We want something along the lines of /dev/sda or /dev/nvme0n1
    but not /dev/sda3 or /dev/nvme0n1p2.
    """
    major, minor = divmod(os.stat('/').st_dev, 256)
    cmd = "lsblk -o path,maj:min | grep {}:0 ".format(major)
    cmd2 = "| awk '{print $1}'"
    return subprocess.check_output(f"{cmd}{cmd2}", shell=True, stderr=subprocess.PIPE). \
        decode(encoding='ascii').strip().__str__()


def is_source_connected(sym_link):
    if os.path.exists("{}".format(sym_link)):
        return True
    else:
        return False


def is_alive(pid):
    try:
        os.kill(pid, 0)
    except OSError:
        return False
    else:
        return True


def is_blkdev_still_valid(target, absolute=True):
    rtn = False
    source_bypath = get_config_setting('source_dev_path')
    if target == get_source_blkdev(source_bypath):
        if is_in_lsblk_list(target, absolute=absolute):
            return True
        else:
            logging.error("Source not found in lsblk(8)?")
            return False
    for usb in get_number_or_list_of_usbs('list', source_bypath, absolute=absolute):
        if usb == target and is_in_lsblk_list(target, absolute=absolute):
            rtn = True
            break
    return rtn


def is_in_lsblk_list(target, absolute=False):
    if absolute:
        cmd = "lsblk -o name -p | grep -v '─' | grep -w "
    else:
        cmd = "lsblk -o name | grep -v '─' | grep -w "

    grep = subprocess.run("{}{}".format(cmd, target),
                          shell=True,
                          stderr=subprocess.PIPE,
                          stdout=subprocess.PIPE).stdout.decode(encoding='utf-8').strip()

    if grep == target:
        return True
    else:
        '''logging.debug("grep = {}, absolute = {}".format(grep, absolute))'''
        return False


def get_source_blkdev(sym_link):
    """ Fix: returns literal sym_link if no device is actually connected. """
    return os.path.realpath("{}".format(sym_link))


def strip_abs_blkdev(abs_blkdev):
    return str(abs_blkdev).split('/')[2]
