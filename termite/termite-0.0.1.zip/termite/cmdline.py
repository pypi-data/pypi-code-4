"""Termite

Usage:
  termite [<user_command>]
  termite (-h | --help)
  termite --version

Options:
  -h --help     Show this screen.
  --version     Show version.

"""
import os
import logging
import time

import yaml

from docopt import docopt

from termite.utils import Watcher
from termite.parser import parse_yaml
from termite.server import Server


import webbrowser
import sys


def main():

    logging.basicConfig(format='%(levelname)s: %(message)s',
                        level=logging.INFO)

    args = docopt(__doc__, version='Termite 0.0.1')
    command = args.get('<user_command>')

    if os.path.exists('termite.yaml'):

        logging.info('-----')
        logging.info('Reading termite.yaml')
        with open('termite.yaml', 'r') as stream:
            elements = yaml.load(stream)

        parse_yaml(elements, command)

        if Watcher.is_empty() and not Watcher.is_server():
            return

        server = None
        if Watcher.is_server():
            server = Server(os.path.join(os.getcwd(), Watcher.server_path))
            webbrowser.open('http://127.0.0.1:8888', new=2, autoraise=True)
        try:
            while True:
                Watcher.check_all()
                time.sleep(1)

        except KeyboardInterrupt:
            logging.info('Exiting...')
            if server:
                server.stop()
            return
    else:

        logging.info('termite.yaml file not found, nothing to do')


def termite_cli():

    function = sys.argv[1]
    args = sys.argv[2:]

    if os.getcwd() not in sys.path:
        sys.path.append(os.getcwd())

    import termite_cli
    getattr(termite_cli, function)(args)
