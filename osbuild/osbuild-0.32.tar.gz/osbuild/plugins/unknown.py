# coding=utf-8

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

from osbuild import distro
from osbuild.plugins import interfaces


class PackageManager(interfaces.PackageManager):
    def __init__(self, test=False, interactive=True):
        pass

    def install_packages(self, packages):
        pass

    def remove_packages(self, packages):
        pass

    def update(self):
        pass

    def find_all(self):
        return []

    def find_with_deps(self, packages):
        return []

distro.register_package_manager("unknown", PackageManager)


class DistroInfo(interfaces.DistroInfo):
    def __init__(self):
        self.lib_dir = None
        self.name = "unknown"
        self.version = "unknown"
        self.gnome_version = "3.4"
        self.valid = True
        self.supported = False

distro.register_distro_info(DistroInfo)
