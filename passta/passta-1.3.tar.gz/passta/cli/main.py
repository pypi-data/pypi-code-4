'''
usage: passta [-f <file>|--file <file>] <command> [<args>...]

Options:
    -f <file>, --file <file>    location of password safe [default: ~/.passta]
    --version                   print version information

The commands are:
    get         retrieve entry
    list        list entries
    remove      remove entry
    store       store entry

See 'passta <command> -h' for more information on a specific command.
'''
import sys

from docopt import docopt

from passta import __version__
from passta.store import Store
from passta.cli import commands


def main():
    args = docopt(
        __doc__, options_first=True, version='passta {}'.format(__version__))

    try:
        store = Store(args['--file'])
    except IOError as e:
        sys.exit(e)

    command = args['<command>']
    try:
        fn = commands[command]
    except KeyError:
        sys.exit('"{}" is not a passta command.'.format(command))
    else:
        argv = [command] + args['<args>']
        fn(store, argv)
