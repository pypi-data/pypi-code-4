# -*- coding: utf-8 -*-

import sys
import os
import logging
from configparser import ConfigParser
from collections import OrderedDict
max_items = 300

# default config can be overrided in config.ini. Uses same format:
DEFAULT_CONFIG = """

[player]
server=
webport = 9000
audioport = 3483
mac=
datapath=

[audioplayers]
squeezelite-pa = squeezelite-pa -s {player[server]}:{player[audioport]} -m {player[mac]} -a 100
squeezelite = squeezelite -s {player[server]}:{player[audioport]} -m {player[mac]} -a 100
squeezelite-win = squeezelite-win.exe -s {player[server]}:{player[audioport]} -m {player[mac]} -a 200

"""


def getuserconfigfile():
    """find user folder"""
    userconfigfolder = os.path.expanduser("~")
    if os.name == 'nt':
        try:
            userconfigfolder = os.environ['APPDATA']
        except KeyError:
            pass
    return os.path.join(userconfigfolder, '.squeezeuirc')

parser = ConfigParser()
parser.read_string(DEFAULT_CONFIG)

# read config-file if exists
for cf in [
    os.path.join(sys.path[0], 'config.ini'),
    os.path.join(os.path.dirname(sys.argv[0]), 'config.ini'),
    getuserconfigfile() ]:
        if os.path.isfile(cf):
            parser.read(cf)

# config sections as dicts.
config = dict(parser.items('player'))
audioplayers = OrderedDict(parser.items('audioplayers'))


def saveuserconfig():
    newconfig = ConfigParser()
    newconfig['player'] = config
    if 'datapath' in newconfig['player']:
        del newconfig['player']['datapath']
    with open(getuserconfigfile(), 'w') as newconfigfile:
        newconfig.write(newconfigfile)


def setuplogging(verbose=True, quiet=False,stream=None,loggingformat=None):
    level=logging.DEBUG if verbose else logging.INFO
    if quiet:
        level = logging.ERROR

    if loggingformat is None:
        loggingformat = '%(asctime)-15s %(levelname)-9s: %(threadName)-11s: %(message)s'
 
    logging.basicConfig(
        #format='%(asctime)-15s %(levelname)-5s:%(name)s:%(message)s',
        format = loggingformat,
        datefmt = '%Y-%m-%d %H:%M:%S', 
        level = level,
        stream = stream)