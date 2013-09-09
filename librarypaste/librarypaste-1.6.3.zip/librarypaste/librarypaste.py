#!/usr/bin/env python
# encoding: utf-8

import os
import argparse

import yaml
import cherrypy

from . import datastore
from .pastebin import (BASE, PasteBinPage, PasteViewPage, LastPage,
    PastePlainPage, FilePage, AboutPage)

def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--config', dest="configs",
        default=[], action="append", help="config file")
    parser.add_argument('--yaml-config', dest="configs",
        type=load_yaml, action="append", help="yaml config")
    parser.add_argument('--yaml-config-env', dest="configs",
        type=load_yaml_env, action="append", help="yaml config")
    return parser.parse_args()

def load_yaml(filename):
    """
    Given a param, load the YAML config from a file.
    """
    return yaml.load(open(filename))

def load_yaml_env(env_var_name):
    """
    Resolve the env var to a filename and load the YAML config from there.
    """
    return load_yaml(os.environ[env_var_name])

def main():
    args = get_args()

    root = PasteBinPage()
    root.about = AboutPage()
    root.plain = PastePlainPage()
    root.last = LastPage()
    root.file = FilePage()
    root.default = PasteViewPage()

    # Cherrypy configuration here
    app_conf = {
        'global': {
            'server.socket_host': '::0',
        },
        '/static': {
            'tools.staticdir.on': True,
            'tools.staticdir.dir': os.path.join(BASE, 'static'),
        },
        'lexers': {'favorites': ['python']},
        'branding': {
            'name': 'Library',
            'logo source': '/static/librarypaste.png',
        }
    }

    app = cherrypy.tree.mount(root=None)
    app.merge(app_conf)
    map(app.merge, args.configs)

    app.config.setdefault('datastore', dict(
        factory = 'librarypaste.jsonstore:JsonDataStore',
        repo = os.path.join(os.getcwd(), 'repo'),
    ))

    # after merging all the configs, initialize the datastore.
    app.config['datastore'].update(
        datastore = datastore.init_datastore(app.config['datastore']),
    )

    cherrypy.quickstart(root, '', config=app.config)

if __name__ == '__main__':
    '''
    Useful for development mode
    '''
    main()
