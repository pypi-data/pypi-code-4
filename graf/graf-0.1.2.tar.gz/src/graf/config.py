#!/usr/bin/env python
# coding=utf-8
"""

(C) 2013 hashnote.net, Alisue
"""
__author__  = 'Alisue (lambdalisue@hashnote.net)'
__version__ = '0.1.0'
__date__    = '2013-10-08'

import os
import yaml
import platform
from os.path import join
from os.path import abspath
from os.path import dirname


"""installed root directory"""
root = abspath(dirname(dirname(dirname(__file__))))
"""system configuration file path"""
config_file = join(root, 'config', 'grafrc')

def get_user_path():
    """get user configuration root directory"""
    system = platform.system()
    if system == 'Windows':
        root = join(os.environ['APPDATA'], 'graf')
        conf = join(root, 'grafrc')
        plug = join(root, 'plugins')
    elif system in ('Linux', 'Darwin'):
        root = join(os.path.expanduser('~'), '.graf')
        conf = root + 'rc'
        plug = join(root, 'plugins')
    else:
        # Unknown
        root = join(os.path.expanduser('~'), 'graf')
        conf = root + 'rc'
        plug = join(root, 'plugins')
    return root, conf, plug

def default_config():
    """create default configuration object"""
    # get user path
    user_root, user_config_file, user_plugin_dirs = get_user_path()
    # create empty ConfigObj by configspec
    conf = {
        'user': {
            'root': user_root,
            'config_file': user_config_file,
            'plugin_dirs': user_plugin_dirs,
        },
        'default': {
            'loader': 'loaders.PlainLoader',
            'parser': 'parsers.PlainParser',
            'linestyles': ['-', '--', '-.'],
            'markerstyles': ['.', 'o', 'x', '*'],
            'colors': None,
        }
    }
    return conf

def load_config():
    """load system and user configuration files"""
    def _load_config(filename):
        if os.path.exists(filename):
            with open(filename, 'r') as f:
                return yaml.safe_load(f.read().decode('utf-8')) or {}
        return {}
    # start from default config
    conf = default_config()
    # load system config
    sys_config = _load_config(config_file)
    conf.update(sys_config)
    # create user root if it is not exists
    if not os.path.exists(conf['user']['root']):
        os.makedirs(conf['user']['root'])
    # load or create user config
    usr_config = _load_config(conf['user']['config_file'])
    conf.update(usr_config)
    return conf

"""settings"""
settings = load_config()

