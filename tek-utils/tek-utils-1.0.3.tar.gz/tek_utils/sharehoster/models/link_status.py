__copyright__ = """ Copyright (c) 2013 Torsten Schmits

This program is free software; you can redistribute it and/or modify it
under the terms of the GNU General Public License as published by the
Free Software Foundation; either version 3 of the License, or (at your
option) any later version.

This program is distributed in the hope that it will be useful, but
WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program; if not, see <http://www.gnu.org/licenses/>.
"""

class LinkStatus(object):

    def __init__(self, response):
        self.result = response.get('result', '')
        self.status = response.get('status', '')

    @property
    def success(self):
        return self.result.lower() == 'success'

    @property
    def error(self):
        return self.status.lower() == 'dead'

__all__ = ['LinkStatus']
