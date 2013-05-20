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

import pkgutil
import imp

from osbuild import config
from osbuild import environ
from osbuild import plugins
from osbuild import system
from osbuild import build
from osbuild import state
from osbuild import clean


def run_build(full=False):
    if full or state.full_build_is_required():
        clean.clean(build_only=True)
        environ.setup_gconf()

    state.full_build_touch()

    if not build.pull(lazy=True):
        return False

    if not build.build(full=False):
        return False

    return True


def load_plugins():
    for loader, name, ispkg in pkgutil.iter_modules(plugins.__path__):
        f, filename, desc = imp.find_module(name, plugins.__path__)
        imp.load_module(name, f, filename, desc)


def setup(config_args, check_args):
    load_plugins()

    config.setup(**config_args)

    if not system.check(**check_args):
        return False

    environ.setup_variables()
    environ.setup_gconf()

    return True
