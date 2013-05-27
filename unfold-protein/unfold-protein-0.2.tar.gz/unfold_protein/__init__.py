# Copyright (C) 2012 W. Trevor King <wking@tremily.us>
#
# This file is part of unfold_protein.
#
# unfold_protein is free software: you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by the Free
# Software Foundation, either version 3 of the License, or (at your option) any
# later version.
#
# unfold_protein is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more
# details.
#
# You should have received a copy of the GNU General Public License along with
# unfold_protein.  If not, see <http://www.gnu.org/licenses/>.

from .config import PackageConfig as _PackageConfig


__version__ = '0.2'


package_config = _PackageConfig(package_name=__name__)
package_config.load_system()
