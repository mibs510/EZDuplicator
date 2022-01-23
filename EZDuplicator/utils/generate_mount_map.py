#!/usr/bin/env python3
"""

Copyright (c) 2021 Connor McMillan <connor@mcmillan.website>. All rights reserved.

This work is licensed under the terms of the MIT license.
For a copy, see <https://opensource.org/licenses/MIT>.

"""
import os
import sys

import EZDuplicator.lib.DataOnlyDuplication
import EZDuplicator.lib.EZDuplicator


def main():
    json_file = EZDuplicator.lib.EZDuplicator.__mounts_map__

    if EZDuplicator.lib.DataOnlyDuplication.grep_mount("/dev/sd"):
        print("*** UNMOUNT ANY NON ESSENTIAL MEDIA FROM THE EZ DUPLICATOR! ***")
        print("*** EITHER: RESTART THE EZ DUPLICATOR OR UNMOUNT(8)! ***")
        sys.exit(1)

    print("*** TO PROCEED, VERIFY THAT THE SOURCE SLOT IS EMPTY! *** ")
    input("*** HIT ENTER TO CONTINUE ***")

    try:
        mount_to_json = EZDuplicator.lib.DataOnlyDuplication.get_mount2json()
    except Exception as ex:
        print(ex)
        sys.exit(1)

    if os.path.isfile(json_file):
        print("Removing existing mount_map.json")
        os.remove(json_file)

    print("")
    print("Generating a JSON serilaized mount map...")

    with open(json_file, 'w', encoding='utf-8') as map_of_ports_json:
        map_of_ports_json.write(mount_to_json)

    return True


if __name__ == '__main__':
    mainret = main()
    sys.exit(mainret)
