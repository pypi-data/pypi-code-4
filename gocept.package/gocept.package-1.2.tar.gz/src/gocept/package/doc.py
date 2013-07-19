# Copyright (c) 2012 gocept gmbh & co. kg
# See also LICENSE.txt

import os
import os.path
import pkg_resources
import sys


def main(argv=sys.argv):
    cwd = os.getcwd()
    sphinx_build = pkg_resources.load_entry_point(
        'Sphinx', 'console_scripts', 'sphinx-build')
    argv = ['sphinx-build'] + argv[1:]
    argv += ['-E', os.path.join(cwd, 'doc'), os.path.join(cwd, 'build', 'doc')]
    sphinx_build(argv)
