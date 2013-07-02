# Copyright (C) 2013 by Barry A. Warsaw
#
# This file is part of world
#
# world is free software: you can redistribute it and/or modify it under the
# terms of the GNU General Public License as published by the Free Software
# Foundation, version 3 of the License.
#
# world is distributed in the hope that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more
# details.
#
# You should have received a copy of the GNU General Public License along with
# world.  If not, see <http://www.gnu.org/licenses/>.

"""Refresh the database."""

__all__ = [
    'refresh',
    ]


import pickle
import logging
import xml.etree.ElementTree as ET

from pkg_resources import resource_filename
try:
    from urllib.request import urlopen
except ImportError:
    # Python 2
    from urllib import urlopen


log = logging.getLogger('world')


def refresh(src, dst=None):
    """Refresh the country code database.

    :param src: The XML file to use as the database source.
    :param dst: The name of the file to pickle the processed database into.
        This is used as a cache for performance.
    """
    if dst is None:
        dst = resource_filename('worldlib.data', 'codes.pck')
    by_code = {}
    with urlopen(src) as source:
        tree = ET.fromstring(source.read())
    for entry in tree:
        if entry.tag != 'ISO_3166-1_Entry':
            log.debug('Skipping unknown top-level tag: {}'.format(entry.tag))
            continue
        name = code = None
        for child in entry:
            if child.tag == 'ISO_3166-1_Country_name':
                name = child.text
            elif child.tag == 'ISO_3166-1_Alpha-2_Code_element':
                code = child.text
            else:
                log.debug('Skipping unknown entry tag: {}'.format(child.tag))
            if name is not None and code is not None:
                by_code[code.lower()] = name
                break
    with open(dst, 'wb') as output:
        # Use protocol 2 for interoperability with Python 2.
        pickle.dump(by_code, output, protocol=2)
