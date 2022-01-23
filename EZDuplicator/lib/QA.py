"""

Copyright (c) 2021 Connor McMillan <connor@mcmillan.website>. All rights reserved.

This work is licensed under the terms of the MIT license.
For a copy, see <https://opensource.org/licenses/MIT>.

"""
import glob
import json
import logging
import os

import EZDuplicator.lib.EZDuplicator


def get_disk_by_path(abs_blkdev):
    try:
        rtn = None
        for disk_by_path in glob.glob("/dev/disk/by-path/pci-*-scsi*"):
            if os.path.islink(disk_by_path):
                if os.readlink(disk_by_path).split("/")[2] == abs_blkdev.split("/")[2]:
                    rtn = disk_by_path
        return rtn
    except Exception as ex:
        logging.error(ex)
        return None


def get_x_and_y(disk_by_path):
    try:
        with open(EZDuplicator.lib.EZDuplicator.__ports_map__) as json_file:
            deserailized_map_of_ports = json.load(json_file)

        columns = 0
        while True:
            try:
                tmp = deserailized_map_of_ports['map_of_ports'][0][columns]
                columns += 1
            except Exception:
                break

        rows = 0
        while True:
            try:
                tmp = deserailized_map_of_ports['map_of_ports'][rows]
                rows += 1
            except Exception:
                break

        for y in range(columns):
            for x in range(rows):
                if deserailized_map_of_ports['map_of_ports'][x][y] == disk_by_path:
                    logging.info("{} = ({},{})".format(disk_by_path, x, y))
                    return "{}{}".format(x, y)
        return None
    except Exception as ex:
        logging.error(ex)
        return None
