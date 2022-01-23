#!/usr/bin/env python3
"""

Copyright (c) 2021 Connor McMillan <connor@mcmillan.website>. All rights reserved.

This work is licensed under the terms of the MIT license.
For a copy, see <https://opensource.org/licenses/MIT>.

"""
import argparse
import os.path
import sys


from EZDuplicator.version import __version__
import EZDuplicator.lib.EZDuplicator

parser = argparse.ArgumentParser(prog="setup.py",
                                 formatter_class=argparse.RawTextHelpFormatter,
                                 epilog="setup.py - EZDuplicator v{}\n"
                                        "(c) 2021 Connor McMillan "
                                        "<connor@mcmillan.website>".format(EZDuplicator.version.__version__),
                                 exit_on_error=False)
parser.add_argument('--post', help='Add a post onto the semantic versioning for the wheel package.\n'
                                   'e.g. EZDuplicator-X.Y.Z.postW-py2.py3-none-any.whl',
                    action='store')

args, unkown = parser.parse_known_args()
sys.argv = [sys.argv[0]] + unkown
from setuptools import setup # noqa


if args.post is not None:
    __version__ = __version__ + "-" + args.post

if os.path.exists("README.md"):
    with open("README.md", "r") as fh:
        long_description = fh.read()

setup(
    name='EZDuplicator',
    version=__version__,
    platforms='linux',
    packages=['EZDuplicator', 'EZDuplicator/12VPM', 'EZDuplicator/lib', 'EZDuplicator/res', 'EZDuplicator/utils'],
    include_package_data=True,
    entry_points={"gui_scripts": ["EZDuplicator = EZDuplicator.EZDuplicator:main"],
                  "console_scripts": ["ezd-update = EZDuplicator.utils.update_ezduplicator:main",
                                      "ezd-generate_mount_map = EZDuplicator.utils.generate_mount_map:main",
                                      "ezd-generate_port_map = EZDuplicator.utils.generate_port_map:main"]},
    url='https://ezduplicator.com',
    license='MIT',
    author='Connor McMillan',
    author_email='connor@mcmillan.website',
    description='A simple GUI application to securely erase, duplicate, and verify USB flash memory in mass.',
    python_requires=">=3.9",
    install_requires=['certifi~=2021.10.8', 'charset-normalizer~=2.0.9', 'elevate~=0.1.3', 'idna~=3.3',
                      'keyboard~=0.13.5', 'numpy~=1.21.4', 'parse~=1.19.0', 'pexpect==4.8.0', 'psutil~=5.8.0',
                      'pycairo~=1.20.1', 'pydbus~=0.6.0', 'PyGObject~=3.42.0', 'pyserial~=3.5',
                      'python-json-logger~=2.0.2', 'requests~=2.26.0', 'sentry-sdk~=1.5.0', 'urllib3~=1.26.7',
                      'xxhash~=2.0.2', 'Yapsy~=1.12.2'],
    classifiers=['Environment :: X11 Applications :: GTK',
                 'Intended Audience :: Manufacturing',
                 'License :: OSI Approved :: MIT License',
                 'Natural Language :: English',
                 'Operating System :: POSIX :: Linux',
                 'Programming Language :: Python :: 3.9',
                 'Topic :: System :: Hardware :: Universal Serial Bus (USB)',
                 'Topic :: System :: Hardware :: Universal Serial Bus (USB) :: Hub',
                 'Topic :: System :: Hardware :: Universal Serial Bus (USB) :: Mass Storage',
                 'Topic :: System :: Hardware :: Universal Serial Bus (USB) :: Miscellaneous'],
)

if __name__ == "__main__":
    pass
