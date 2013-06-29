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
import shutil
import sys

from django.core.management.base import CommandError, _make_writeable


def copy_helper(style, name, directory):
    """
    Copies the project template into the specified directory.

    """
    # style -- A color style object (see django.core.management.color).
    # name -- The name of the project.
    # directory -- The directory to which the layout template should be copied.
    import re
    from player import settings as player_settings
    if not re.search(r'^[_a-zA-Z]\w*$', name):  # If it's not a valid directory name.
        # Provide a smart error message, depending on the error.
        if not re.search(r'^[_a-zA-Z]', name):
            message = 'make sure the name begins with a letter or underscore'
        else:
            message = 'use only numbers, letters and underscores'
        raise CommandError("%r is not a valid project name. Please %s." % (name, message))
    top_dir = os.path.join(directory, name)
    try:
        os.mkdir(top_dir)
    except OSError, e:
        raise CommandError(e)

    player_root = player_settings.PLAYERDIR

    skel_dir = os.path.join(player_root, 'skel', 'project')

    # Copy project template
    copy_dir(skel_dir, top_dir, name, False, style)


def remove_dst_if_exist(dst):
    if os.path.exists(dst):
        if os.path.islink(dst) or os.path.isfile(dst):
            os.remove(dst)
        else:
            shutil.rmtree(dst)


def copy_dir(source, dest, name, remove_if_exists, style, link=False):
    """ Copy directory recursively from a template directory """
    if remove_if_exists:
        remove_dst_if_exist(dest)
        os.makedirs(dest)

    for d, subdirs, files in os.walk(source):
        relative_dir = d[len(source) + 1:].replace('project_name', name)
        new_relative_dir = os.path.join(dest, relative_dir)
        if not os.path.exists(new_relative_dir):
            os.makedirs(new_relative_dir)
        for i, subdir in enumerate(subdirs):
            if subdir.startswith('.'):
                del subdirs[i]
        for f in files:
            if f.endswith('.pyc'):
                continue
            path_old = os.path.join(d, f)
            path_new = os.path.join(dest, relative_dir, f.replace('project_name', name))
            fp_old = open(path_old, 'r')
            fp_new = open(path_new, 'w')
            fp_new.write(fp_old.read().replace('{{ project_name }}', name))
            fp_old.close()
            fp_new.close()
            try:
                shutil.copymode(path_old, path_new)
                _make_writeable(path_new)
            except OSError:
                sys.stderr.write(style.NOTICE("Notice: Couldn't set permission bits on %s. You're probably using an uncommon filesystem setup. No problem.\n" % path_new))
