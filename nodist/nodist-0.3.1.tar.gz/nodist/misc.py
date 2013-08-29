# coding=utf-8
# nodist is a Node.js version manager.
# Copyright (C) 2013  Kerem Çakırer

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

import os
import re

def version_exists(version):
    nodist_prefix = get_nodist_prefix()
    version_bin_path = os.path.join(get_version_path(version) , "bin")
    if os.path.isdir(version_bin_path):
        return True
    else:
        return False

def create_nodist_prefix():
    nodist_prefix = get_nodist_prefix()
    if not os.path.isdir(nodist_prefix):
        os.mkdir(nodist_prefix)
        os.mkdir(os.path.join(nodist_prefix, "nodes"))
        os.mkdir(get_logs_path())

def get_bin_path():
    link_path = os.path.join(get_nodist_prefix(), "bin")
    return link_path

def get_version_path(version):
    nodist_prefix = get_nodist_prefix()
    version_path = os.path.join(nodist_prefix, "nodes", version)
    return version_path

def get_nodist_prefix():
    if os.geteuid() == 0:
        nodist_prefix = '/usr/local/nodist'
    else:
        home = os.getenv("HOME")
        nodist_prefix = os.path.join(home, ".nodist")
    return nodist_prefix

def valid_version(version):
    if not re.match('^(\d+)\.(\d+)\.(\d+)$', version):
        return False
    else:
        return True

def get_logs_path():
    nodist_prefix = get_nodist_prefix()
    return os.path.join(nodist_prefix, "logs")
