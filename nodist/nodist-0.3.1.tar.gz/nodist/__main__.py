# coding=utf-8
# nodist is a Node.js version manager.
# Copyright (C) 2013  Kerem Çak¿rer

# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.
import sys

from . import __version__
from . import cli
from . import misc

def help_me():
    help_str = """nodist %s
Usage: nodist <version> [options]

Install the specified Node.js version
or if it already is installed, make it the default.

Options:
    -d, --delete      Removes the specified Node.js version.
    -l, --log         Saves the output of the building process to {prefix}/logs

""" % __version__
    sys.stdout.write(help_str)

def main(args):
    misc.create_nodist_prefix()
    if len(args) == 0:
        help_me()
        sys.exit(0)
    else:
        cli.parse(args)

if __name__ == "__main__":
    main(sys.argv[1:])
