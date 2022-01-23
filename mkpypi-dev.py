#!/usr/bin/env python3
"""

Copyright (c) 2021 Connor McMillan <connor@mcmillan.website>. All rights reserved.

This work is licensed under the terms of the MIT license.
For a copy, see <https://opensource.org/licenses/MIT>.

"""
import configparser
from bs4 import BeautifulSoup
import os.path
from pathlib import Path
from subprocess import Popen
import requests.auth
import requests
import sys

__homedir__ = os.path.expanduser('~')
__pypi__ = __homedir__ + "/.pypirc"
__root_dir__ = str(Path(__file__).parent.absolute())


def main() -> int:
    try:
        if Path(__pypi__).is_file:
            os.system("py3clean {}".format(__root_dir__))
            username = get_config_setting("username")
            password = get_config_setting("password")
            repository = get_config_setting("repository") + "packages/"
            post = get_latest_post(username, password, repository)
            Popen("py3clean .", stdout=sys.stdout, stderr=sys.stderr, shell=True).communicate()
            Popen("rm -rf build && rm -rf dist && rm -rf *.egg-info", stdout=sys.stdout,
                  stderr=sys.stderr, shell=True).communicate()
            Popen("python3.9 setup.py --post {} sdist bdist_wheel --universal upload -r dev".format(post),
                  stdout=sys.stdout, stderr=sys.stderr, shell=True).communicate()
            Popen("py3clean .", stdout=sys.stdout, stderr=sys.stderr, shell=True).communicate()
            Popen("rm -rf build && rm -rf dist && rm -rf *.egg-info", stdout=sys.stdout,
                  stderr=sys.stderr, shell=True).communicate()
        else:
            print("Error: Could not find {}".format(__pypi__))
            print("Error: Visit https://help.ezduplicator.com to download pypirc")
            return 1
    except Exception as ex:
        print("Exception: {}".format(ex))
        return 1
    return 0


def get_latest_post(username, password, repository) -> int:
    url = repository
    html = requests.get(url, auth=requests.auth.HTTPBasicAuth(username, password)).content
    soup = BeautifulSoup(html, 'html.parser')
    whl = soup.find_all('a')[-1].text
    post = whl.split('-')
    post = post[1]
    post = post.split('.')
    if len(post) <= 3:
        return 1
    post = post[3]
    post = post.replace('post', '')
    return int(post) + 1


def get_config_setting(setting) -> str:
    try:
        config = configparser.ConfigParser(interpolation=None)
        config.read(__pypi__)
        if config.has_option('dev', setting):
            return config['dev'][setting]
        else:
            raise Exception("Key {} not found in {}!".format(setting, __pypi__))
    except Exception as ex:
        raise Exception(ex)


if __name__ == '__main__':
    mainret = main()
    sys.exit(mainret)
