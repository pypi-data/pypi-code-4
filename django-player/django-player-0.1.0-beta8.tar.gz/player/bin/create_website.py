#!/usr/bin/env python

# Copyright (c) 2010 by Yaco Sistemas
#
# This file is part of django-player.
#
# django-player is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# django-player is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with django-player.  If not, see <http://www.gnu.org/licenses/>.

import os
import stat
import re
from random import choice
from optparse import OptionParser

from django.core.management.base import CommandError
from django.core.management.color import color_style
from django.utils.importlib import import_module

from player.base.management.base import copy_helper


def create_website(project_name, verbose=False):
    # Determine the project_name a bit naively -- by looking at the name of
    # the parent directory.
    directory = os.getcwd()

    # Check that the project_name cannot be imported.
    try:
        import_module(project_name)
    except ImportError:
        pass
    else:
        raise CommandError("%r conflicts with the name of an existing Python module and cannot be used as a project name. Please try another name." % project_name)

    copy_helper(color_style(), project_name, directory)

    # Create a random SECRET_KEY hash, and put it in the main settings.
    main_settings_file = os.path.join(directory, project_name, 'settings.py')
    settings_contents = open(main_settings_file, 'r').read()
    fp = open(main_settings_file, 'w')
    secret_key = ''.join([choice('abcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*(-_=+)') for i in range(50)])
    settings_contents = re.sub(r"(?<=SECRET_KEY = ')'", secret_key + "'", settings_contents)
    fp.write(settings_contents)
    fp.close()
    # set manage.py as an executable file
    manage_file_path = os.path.join(directory, project_name, 'manage.py')
    mode = os.stat(manage_file_path)[stat.ST_MODE]
    os.chmod(manage_file_path, mode | stat.S_IXUSR)


def main():
    usage = "usage: %prog [options] project_name"
    parser = OptionParser(usage)
    parser.add_option("-q", "--quiet",
                  action="store_false", dest="verbose", default=True,
                  help="don't print status messages to stdout")
    (options, args) = parser.parse_args()
    if len(args) != 1:
        parser.error("You need to define the project name to create")
    create_website(args[0], options.verbose)


if __name__ == "__main__":
    main()
