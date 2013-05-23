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


class PackageManager:
    """Package management"""

    def install_packages(self, packages):
        """Install packages.

           :param packages: packages to install
        """

    def remove_packages(self, packages):
        """Remove a list of packages.

           :param packages: packages to remove
        """

    def update(self):
        """Update packages to the latest version."""

    def find_all(self):
        """Return all the installed packages."""

    def find_with_deps(self, package_names):
        """Return all the installed dependencies of a list of packages.
           The packages itself are also returned in the list.

           :param packages_name: names of the packages to find
           :returns: list of packages with all the dependencies
        """


class DistroInfo:
    """Informations about the distribution"""

    def __init__(self):
        self.name = None
        """The distribution name."""

        self.version = None
        """The distribution version."""

        self.gnome_version = None
        """The major version of GNOME shipped with the distribution."""

        self.valid = False
        """If set to True we are running on this distribution and the
           attributes are all valid.
        """

        self.lib_dir = False
        """Path to the architecture specific lib directory, relative
           to the prefix.
        """

        self.supported = False
        """If set to Trye the distribution is supported."""
