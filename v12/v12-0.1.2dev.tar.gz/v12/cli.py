import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

import argparse
from v12 import env, PackageManager


def install():
    if not env.dev:
        print "installing " + args.package + " ..."
        PackageManager.install(args.package)


def uninstall():
    if not env.dev:
        print "uninstalling " + args.package + " ..."
        PackageManager.uninstall(args.package)

# create the top-level parser
main_parser = argparse.ArgumentParser()
main_parser.add_argument('--dev', '-d', action='store_true')
subparsers = main_parser.add_subparsers(title='subcommands',
                                        description="use `v12 [subcommand] -h` for additional information",
                                        help="subcommand list")

# create the parser for the "install" command
install_parser = subparsers.add_parser('install', help='installs a package from pypi to lib/packages')
install_parser.add_argument('package', help='The package to install. This string can also contain version information in the format pip uses.')
install_parser.set_defaults(func=install)

# create the parser for the "uninstall" command
uninstall_parser = subparsers.add_parser('uninstall', help='uninstalls a package from lib/packages as well as its unused dependencies')
uninstall_parser.add_argument('package', help='The package to install.')

args = main_parser.parse_args()
env.dev = args.dev


args.func()