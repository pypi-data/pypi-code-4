#!/usr/bin/env python
# -*- coding: utf-8 -*-

##############################################################################
# Copyright (C) 2013 NaN·tic
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
##############################################################################
import argparse
import glob
import sys
from path import path
from sphinx.util.console import bold, nocolor, color_terminal

from .quickstart import choice, do_prompt, is_path

# function to get input from terminal -- overridden by the test suite
try:
    # this raw_input is not converted by 2to3
    term_input = raw_input
except NameError:
    term_input = input


def create_symlinks(modules_path, lang, root, remove=True):
    if remove:
        # Removing existing symlinks
        for root_file in path(root).listdir():
            if root_file.islink():
                print "removing %s" % root_file
                root_file.remove()

    for module_doc_dir in glob.glob('%s/*/doc/%s' % (modules_path, lang)):
        print "symlink to %s" % module_doc_dir
        module_name = str(path(module_doc_dir).parent.parent.basename())
        symlink = path(root).joinpath(module_name)
        if not symlink.exists():
            path(root).relpathto(path(module_doc_dir)).symlink(symlink)


def main(argv=sys.argv):
    if not color_terminal():
        nocolor()

    d = {}
    parser = argparse.ArgumentParser()
    parser.add_argument('lang_code')
    parser.add_argument('modules_path')
    parser.add_argument('root', default='.')
    parser.add_argument('--no-remove', action='store_false', dest='remove',
        default=True, help='Do not remove existing symlinks in root')
    options = parser.parse_args()

    d['lang'] = options.lang_code
    d['modules_path'] = options.modules_path
    d['path'] = options.root
    try:
        print bold('Welcome to the Trydoc symlinks creation utility.')
        print '''
Please enter values for the following settings (just press Enter to
accept a default value, if one is given in brackets).'''

        if 'modules_path' in d:
            print bold('''
Selected modules path: %s''' % d['modules_path'])
        else:
            print '''
Enter the modules sources path where found the documentation.'''
            do_prompt(d, 'modules_path',
                'Modules sources path where found the documentation',
                '../trytond/trytond/modules', is_path)

        if 'lang' in d:
            print bold('''
    Selected language: %s''' % d['lang'])
        else:
            print '''
    Enter the language code for documentation.'''
            do_prompt(d, 'lang', 'Language code for the documentation', 'es',
                    choice(['es']))

        if 'path' in d:
            print bold('''
Selected root path: %s''' % d['path'])
        else:
            print '''
Enter the root path for documentation.'''
            do_prompt(d, 'path', 'Root path of the documentation', '.',
                is_path)
    except (KeyboardInterrupt, EOFError):
        print
        print '[Interrupted.]'
        return

    create_symlinks(d['modules_path'], d['lang'], d['path'], options.remove)
