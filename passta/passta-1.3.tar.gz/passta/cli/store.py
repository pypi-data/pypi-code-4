'''
usage: passta store <entry>
'''
import sys
from getpass import getpass

from docopt import docopt


def get_password(entry):
    while True:
        password = getpass('Password for {}: '.format(entry))
        password_again = getpass('Password for {} again: '.format(entry))
        if password == password_again:
            return password
        else:
            print(
                'Passwords did not match! Please try again.', file=sys.stderr)


def do_store(store, argv):
    args = docopt(__doc__, argv=argv)
    entry = args['<entry>']
    try:
        store['passwords'][entry] = get_password(entry)
    except (KeyboardInterrupt, EOFError):
        sys.exit('Interrupted')
    store.save()
