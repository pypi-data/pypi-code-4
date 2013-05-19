# Copyright 2013 Daniel Narvaez
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os
import subprocess

from osbuild import config
from osbuild import command
from osbuild import xvfb
from osbuild import build

_checkers = {}


def check_one(module_name):
    for module in config.load_modules():
        if module.name == module_name:
            return _check_module(module)

    return False


def check():
    if not build.build():
        return False

    modules = config.load_modules()
    for module in modules:
        if not _check_module(module):
            return False

    return True


def _check_module(module):
    build_system = module.get_build_system()

    if build_system and module.has_checks:
        print("* Checking %s" % module.name)
        return _checkers[build_system](module)

    return True


def _volo_checker(module):
    orig_root = module.get_source_dir()
    for root, dirs, files in os.walk(module.get_source_dir()):
        if root == orig_root and "lib" in dirs:
            dirs.remove("lib")
        for f in files:
            if f.endswith(".js"):
                try:
                    command.run(["jshint", os.path.join(root, f)])
                except subprocess.CalledProcessError:
                    return False
    return True

_checkers['volo'] = _volo_checker


def _autotools_checker(module):
    result = True
    os.chdir(module.get_source_dir())
    xvfb_proc, orig_display = xvfb.start()

    try:
        command.run(["dbus-launch", "--exit-with-session",
                     "make", "check"])
    except subprocess.CalledProcessError:
        result = False

    xvfb.stop(xvfb_proc, orig_display)

    return result

_checkers['autotools'] = _autotools_checker
