'''
usage: passta get [-c|--clipboard] [--] <entry>

Options:
    -c, --clipboard         copy password to clipboard
'''
import sys

from docopt import docopt

from passta.clipboard import copy, ClipboardError


def do_get(store, argv):
    args = docopt(__doc__, argv=argv)
    entry = args['<entry>']
    try:
        password = store['passwords'][entry]
    except KeyError:
        sys.exit('Entry "{}" not found.'.format(entry))
    if args['--clipboard']:
        try:
            copy(password)
        except ClipboardError as e:
            sys.exit(e)
    else:
        print(password)
