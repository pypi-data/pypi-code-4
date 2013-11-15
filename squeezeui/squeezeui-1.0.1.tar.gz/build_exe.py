#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
#  Squeezeui - Graphical user interface for Squeezebox players.

import os
import sys
from cx_Freeze import setup, Executable
if len(sys.argv) == 1:
    sys.argv.append('build')

base = None
if sys.platform == "win32":
    base = "Win32GUI"

build_exe_options = {
    "includes": ['atexit'],
    "include_files": ['squeezeui/views'],
    "compressed": True,
    "copy_dependent_files": True
}

install_exe_options = {
    "install_dir": "released"
}

setup(name='squeezeui',
    version='1.0.1',
    description='Graphical user interface for Squeezebox players.',
    long_description=open('README').read(),
    author='Frode Holmer',
    author_email='fholmer@gmail.com',
    license='GPLv3',
    url='https://bitbucket.org/fholmer/squeezeui',
    keywords='Squeezebox Squeezelite',
    options = {
        "build_exe": build_exe_options,
        "install_exe": install_exe_options
    },
    executables = [Executable(script = "bin/squeezeui-player-exe.py",
                                  base = base,
                                  targetName = 'squeezeui-player.exe',
                                  compress = True,
                                  copyDependentFiles = True),
                   Executable(script = "bin/squeezeui-controller-exe.py",
                                  base = base,
                                  targetName = 'squeezeui-controller.exe',
                                  compress = True,
                                  copyDependentFiles = True)])
