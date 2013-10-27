#!/usr/bin/env python
import sys
from os.path import basename, exists
import shelve
import json
from jsonpickle.pickler import Pickler


def main(argv):
    if len(argv) != 2:
        print('error: usage: {} [shelvefile]'.format(basename(argv[0])))
        return 1

    if not exists(sys.argv[1]):
        print('error: file does not exist: {}'.format(sys.argv[1]))
        return 2

    shelf = shelve.open(sys.argv[1])
    print(json.dumps(Pickler().flatten(dict(shelf)), indent=2))


def run():
    sys.exit(main(sys.argv) or 0)


if __name__ == '__main__':
    run()