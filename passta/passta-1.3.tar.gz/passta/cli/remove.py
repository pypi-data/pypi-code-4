'''
usage: passta remove <entry>
'''
from docopt import docopt


def do_remove(store, argv):
    args = docopt(__doc__, argv=argv)
    store['passwords'].pop(args['<entry>'], None)
    store.save()
