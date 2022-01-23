"""

Copyright (c) 2021 Connor McMillan <connor@mcmillan.website>. All rights reserved.

This work is licensed under the terms of the MIT license.
For a copy, see <https://opensource.org/licenses/MIT>.

"""
import sys
from pathlib import Path

this_dir = Path(__file__).parent.absolute()
ezduplicator_dir = str(Path(this_dir).parent.absolute())
ezduplicator_lib_dir = ezduplicator_dir + "/lib"
site_packages = str(Path(ezduplicator_dir).parent.absolute())
sys.path.insert(1, ezduplicator_dir)
