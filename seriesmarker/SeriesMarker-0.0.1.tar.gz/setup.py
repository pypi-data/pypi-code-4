#==============================================================================
# -*- coding: utf-8 -*-
#
# Copyright (C) 2013 Tobias Röttger <toroettg@gmail.com>
#
# This file is part of SeriesMarker.
#
# SeriesMarker is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 3 as
# published by the Free Software Foundation.
#
# SeriesMarker is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with SeriesMarker.  If not, see <http://www.gnu.org/licenses/>.
#==============================================================================

import sys
import os

# Sets variables starting with 'application'; avoids the import of
# config.py in case dependencies are not available on system.
with open("seriesmarker/util/config.py") as f:
    content = [line.strip() for line in f.readlines() if line.startswith("application")]
for assignment in content:
    exec(assignment)

if len(sys.argv) > 1 and sys.argv[1] == "bdist_msi":
    try:
        global setup
        from cx_Freeze import setup, Executable
        import pytvdbapi, PySide, appdirs, sqlalchemy
    except ImportError as e:
        raise SystemExit("Missing module '{}'. Please install required modules"
            " before trying to build a binary distribution.".format(e.name))

    plugins_path = os.path.relpath(os.path.join(os.path.dirname(PySide.__file__), "plugins"))
    pytvdb_path = os.path.relpath(os.path.join(os.path.dirname(pytvdbapi.__file__)))

    include_files = [
        (os.path.join(pytvdb_path, "data"), "data"),
        (os.path.join(plugins_path, "imageformats"), os.path.join("plugins", "imageformats")),
        (os.path.join("resources", "qt.conf"), "qt.conf")
    ]

    packages = [
        "sqlalchemy.dialects.sqlite"
    ]

    exe = Executable(
        script='bin/seriesmarker',
        base='Win32GUI'
    )

    # http://msdn.microsoft.com/en-us/library/windows/desktop/aa371847(v=vs.85).aspx
    shortcut_table = [
        (
            "ProgramMenuShortcut",  # Shortcut
            "ProgramMenuFolder",  # Directory_
            "SeriesMarker",  # Name
            "TARGETDIR",  # Component_
            "[TARGETDIR]seriesmarker.exe",  # Target
            None,  # Arguments
            application_description,  # Description @UndefinedVariable
            None,  # Hotkey
            None,  # Icon
            None,  # IconIndex
            None,  # ShowCmd
            'TARGETDIR'  # WkDir
        ),
        (
            "DesktopShortcut",  # Shortcut
            "DesktopFolder",  # Directory_
            "SeriesMarker",  # Name
            "TARGETDIR",  # Component_
            "[TARGETDIR]seriesmarker.exe",  # Target
            None,  # Arguments
            None,  # Description
            None,  # Hotkey
            None,  # Icon
            None,  # IconIndex
            None,  # ShowCmd
            'TARGETDIR'  # WkDir
        )
    ]

    msi_data = dict(
        Shortcut=shortcut_table
    )

    bdist_msi = dict(
        data=msi_data
    )

    options = dict(
        include_files=include_files,
        packages=packages,
    )

    specific_arguments = {
        "executables": [exe],
        "options": {'build_exe': options, 'bdist_msi': bdist_msi}
    }
else:
    import inspect
    global setup

    # Imports distribute_setup from the tools directory without
    # the need of converting it to a python package.
    cmd_subfolder = os.path.realpath(os.path.abspath(os.path.join(
        os.path.split(inspect.getfile(inspect.currentframe()))[0], "tools")))
    if cmd_subfolder not in sys.path:
        sys.path.insert(0, cmd_subfolder)

    try:
        from setuptools import setup
    except ImportError:
        from distribute_setup import use_setuptools
        use_setuptools()
        from setuptools import setup

    packages = [
        'seriesmarker',

        'seriesmarker.gui',
        'seriesmarker.gui.model',
        'seriesmarker.gui.model.search',
        'seriesmarker.gui.resources',

        'seriesmarker.net',

        'seriesmarker.persistence',
        'seriesmarker.persistence.model',
        'seriesmarker.persistence.factory',

        'seriesmarker.util'
    ]

    scripts = [
        'bin/seriesmarker',
    ]

    specific_arguments = {
        "packages": packages,
        "scripts": scripts,
    }

classifiers = [
    'Development Status :: 3 - Alpha',
    'Environment :: X11 Applications',
    'Environment :: X11 Applications :: Qt',
    'Environment :: Win32 (MS Windows)',
    'Environment :: MacOS X',
    'Intended Audience :: End Users/Desktop',
    'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
    'Operating System :: POSIX :: Linux',
    'Operating System :: Microsoft :: Windows',
    'Operating System :: MacOS :: MacOS X',
    'Programming Language :: Python',
    'Programming Language :: Python :: 3',
    'Topic :: Multimedia',
    'Topic :: Utilities '
]

common_arguments = {
    "name": application_name,  # @UndefinedVariable
    "version": application_version,  # @UndefinedVariable

    "author": application_author_name,  # @UndefinedVariable
    "author_email": application_author_email,  # @UndefinedVariable
    "url": application_url,  # @UndefinedVariable

    "description": application_description,  # @UndefinedVariable
    "long_description": open('README').read(),

    "license": application_license,  # @UndefinedVariable
    "install_requires": application_dependencies,  # @UndefinedVariable
    "platforms": ["any"],
    "classifiers": classifiers
}

arguments = dict(common_arguments)
arguments.update(specific_arguments)

setup(**arguments)
