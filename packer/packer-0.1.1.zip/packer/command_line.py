#!/usr/bin/python
"""Packer

Usage:
    packer list
    packer search <name>
    packer install [-f | --force] <name>
    packer uninstall [-f | --force] <name>
    packer rebuild [-f | --force]
    packer (-h | --help)
    packer (-v | --version)

Options:
    -h, --help       Show this screen.
    -v, --version    Show version.
    -f, --force      Force action.

"""
from docopt import docopt
from packer import Packer


class TerminalPacker(Packer):

    def __init__(self):
        # Parse using Docopt
        args = docopt(__doc__, version='{} v{}'.format(self.name, self.version))
        self.args = args
        # Parse options
        self.options = {}
        self.options['name'] = args.get('<name>')
        super(TerminalPacker, self).__init__()

    def run(self):
        args = self.args
        if args['list']:
            self.list()
        elif args['search']:
            self.search()
        # elif args['install']:
            # pack.install()
        # elif args['uninstall']:
            # pack.uninstall()
        else:
            raise NotImplementedError()

    def list(self):
        print 'Listing installed packages:'
        packages = super(TerminalPacker, self).list()
        for p in packages:
            print '\n{}'.format(p)
        print '\n{} packages total'.format(len(packages))

    def search(self):
        pkg = self.options['name']
        print 'Searching for package {}...'.format(pkg)
        resp = super(TerminalPacker, self).search(pkg)
        print resp


def main():
    app = TerminalPacker()
    app.run()
    app.close()
