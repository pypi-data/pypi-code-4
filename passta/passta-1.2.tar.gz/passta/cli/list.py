'''
usage: passta list [--] [<pattern>]
'''
import sys
import re

from docopt import docopt


def do_list(store, argv):
    args = docopt(__doc__, argv=argv)
    pattern = args['<pattern>']
    if pattern:
        try:
            pattern = re.compile(pattern)
        except re.error as e:
            sys.exit('re error: {}'.format(e))
    for entry in sorted(store['passwords'].keys()):
        if not pattern or pattern.search(entry):
            print(entry)
