# Copyright (C) 2012-2013 Peter Hatina <phatina@redhat.com>
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, see <http://www.gnu.org/licenses/>.

from setuptools import setup
from lmi.shell import __version__

setup(
    name="openlmi-tools",
    description="OpenLMI (non)interactive shell",
    version=__version__,
    license="GPLv2+",
    url="http://fedorahosted.org/openlmi/",
    author="Peter Hatina",
    author_email="phatina@redhat.com",
    namespace_packages=['lmi'],
    packages=["lmi", "lmi.shell"],
    install_requires=["openlmi"],
    scripts=["lmishell"]
)
