#!/usr/bin/python
# -*- coding: utf-8 -*-

# Hive Automium System
# Copyright (C) 2008-2012 Hive Solutions Lda.
#
# This file is part of Hive Automium System.
#
# Hive Automium System is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Hive Automium System is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Hive Automium System. If not, see <http://www.gnu.org/licenses/>.

__author__ = "João Magalhães <joamag@hive.pt>"
""" The author(s) of the module """

__version__ = "1.0.0"
""" The version of the module """

__revision__ = "$LastChangedRevision$"
""" The revision number of the module """

__date__ = "$LastChangedDate$"
""" The last change date of the module """

__copyright__ = "Copyright (c) 2008-2012 Hive Solutions Lda."
""" The copyright for the module """

__license__ = "GNU General Public License (GPL), Version 3"
""" The license for the module """

import os
import zipfile
import tarfile
import subprocess

import atm

def compress(folder, target = None):
    zip(folder + ".zip", (folder,))
    tar(folder + ".tar", (folder,))
    tar(folder + ".tar.gz", (folder,), compress = True)
    if not target: return
    atm.move(folder + ".zip", target)
    atm.move(folder + ".tar", target)
    atm.move(folder + ".tar.gz", target)

def deb(path = None, **kwargs):
    path = path or os.getcwd()

    debian_path = os.path.join(path, "DEBIAN")
    control_path = os.path.join(debian_path, "control")
    if not os.path.exists(debian_path): os.makedirs(debian_path)

    name = kwargs.get("name") or atm.conf("name", "default")
    version = kwargs.get("version") or atm.conf("version", "0.0.0")
    section = kwargs.get("section") or atm.conf("section", "devel")
    priority = kwargs.get("priority") or atm.conf("priority", "optional")
    arch = kwargs.get("arch") or atm.conf("arch", "all")
    depends = kwargs.get("depends") or atm.conf("depends", "")
    size = kwargs.get("size") or atm.conf("size", "0")
    author = kwargs.get("author") or atm.conf("author", "default")
    description = kwargs.get("description") or atm.conf("description", "")
    contents = atm.DEB_CONTROL % (
        name,
        version,
        section,
        priority,
        arch,
        depends,
        size,
        author,
        description
    )

    file = open(control_path, "wb")
    try: file.write(contents)
    finally: file.close()

    result = subprocess.call([
        "dpkg-deb",
        "--build",
        path
    ])
    if not result == 0: raise RuntimeError("Debian file package operation failed")

def capsule(path, data_path, name = None, description = None):
    name = name or atm.conf("name_cap", "default")
    description = description or atm.conf("description", "default")

    result = subprocess.call([
        "capsule",
        "clone",
        path
    ])
    if not result == 0: raise RuntimeError("Capsule clone operation failed")

    result = subprocess.call([
        "capsule",
        "extend",
        path,
        name,
        description,
        data_path
    ])
    if not result == 0: raise RuntimeError("Capsule extend operation failed")

def colony(descriptor = "plugin.json"):
    result = subprocess.call([
        "colony_admin",
        "build",
        descriptor
    ])
    if not result == 0: raise RuntimeError("Colony build operation failed")

def zip(name, names = None):
    path = os.getcwd()
    names = names or os.listdir(path)
    _zip = zipfile.ZipFile(file = name, mode = "w")
    try:
        for _name in names:
            is_dir = os.path.isdir(_name)
            if is_dir:
                base_name = os.path.basename(_name)
                root_size = len(_name) - len(base_name)
                for base, _dirs, files in os.walk(_name):
                    for file in files:
                        path = os.path.join(base, file)
                        _zip.write(path, path[root_size:])
            else:
                _zip.write(_name)
    finally:
        _zip.close()

def tar(name, names = None, compress = False):
    path = os.getcwd()
    names = names or os.listdir(path)
    _tar = tarfile.open(name = name, mode = compress and "w:gz" or "w")
    try:
        for _name in names: _tar.add(_name)
    finally:
        _tar.close()
