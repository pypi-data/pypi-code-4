__copyright__ = """ Copyright (c) 2010-2011 Torsten Schmits

This program is free software; you can redistribute it and/or modify it under
the terms of the GNU General Public License as published by the Free Software
Foundation; either version 3 of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful, but WITHOUT ANY
WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR
A PARTICULAR PURPOSE. See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License along with this
program; if not, see <http://www.gnu.org/licenses/>.

"""

import vobject, logging

from tek import logger

vobject.base.logger.setLevel(logging.CRITICAL)

def make_vcard(name, email):
    c = vobject.vCard()
    c.add('n')
    c.n.value = vobject.vcard.Name(*reversed(name.split()))
    c.add('fn')
    c.fn.value = name
    c.add('email')
    c.email.value = email
    c.email.type_param = 'INTERNET'
    return c

class VCard(list):
    def __init__(self, path=None):
        list.__init__(self, [])
        if path is not None:
            try:
                with open(path) as file:
                    self[:] = vobject.readComponents(file,
                                                     ignoreUnreadable=True)
            except Exception as e:
                logger.error('Error reading file "{}": {}'.format(path, e))

    def has_name(self, name):
        return any(c.fn.value == name for c in self)

    def pretty(self):
        for c in self:
            c.prettyPrint()

    def add(self, name, email):
        """ Add an entry to the vcard. """
        if not self.has_name(name):
            self.append(make_vcard(name, email))

    def write(self, filename):
        with open(filename, 'w') as f:
            f.writelines(c.serialize() for c in self)
