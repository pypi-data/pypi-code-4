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
import json

from osbuild import config
from osbuild import sourcestamp

_BUILT_MODULES = "builtmodules"
_FULL_BUILD = "fullbuild"
_SYSTEM_CHECK = "syscheck"


def built_module_touch(module):
    built_modules = _load_state(_BUILT_MODULES, {})

    source_stamp = sourcestamp.compute(module.get_source_dir())
    built_modules[module.name] = {"source_stamp": source_stamp}

    _save_state(_BUILT_MODULES, built_modules)


def built_module_is_unchanged(module):
    built_modules = _load_state(_BUILT_MODULES, {})
    if module.name not in built_modules:
        return False

    built_module = built_modules[module.name]
    if "source_stamp" not in built_module:
        return False

    old_source_stamp = built_module["source_stamp"]
    new_source_stamp = sourcestamp.compute(module.get_source_dir())

    return old_source_stamp == new_source_stamp


def system_check_is_unchanged():
    system_check = _load_state(_SYSTEM_CHECK)
    if not system_check or not "config_stamp" in system_check:
        return False

    config_stamp = sourcestamp.compute(config.config_dir)

    return system_check["config_stamp"] == config_stamp


def system_check_touch():
    system_check = _load_state(_SYSTEM_CHECK, {})

    config_stamp = sourcestamp.compute(config.config_dir)
    system_check["config_stamp"] = config_stamp

    _save_state(_SYSTEM_CHECK, system_check)


def full_build_is_required():
    full_build = _load_state(_FULL_BUILD)
    if not full_build:
        return False

    return not (full_build["last"] == config.get_full_build())


def full_build_touch():
    full_build = _load_state(_FULL_BUILD, {})
    full_build["last"] = config.get_full_build()
    _save_state(_FULL_BUILD, full_build)


def clean(build_only=False):
    print("* Deleting state")

    names = [_BUILT_MODULES, _FULL_BUILD]
    if not build_only:
        names.append(_SYSTEM_CHECK)

    for name in names:
        try:
            os.unlink(_get_state_path(name))
        except OSError:
            pass


def _get_state_path(name):
    return os.path.join(config.build_state_dir, "%s.json" % name)


def _load_state(name, default=None):
    state = default

    try:
        with open(_get_state_path(name)) as f:
            state = json.load(f)
    except IOError:
        pass

    return state


def _save_state(name, state):
    with open(_get_state_path(name), "w+") as f:
        json.dump(state, f, indent=4)
        f.write('\n')
