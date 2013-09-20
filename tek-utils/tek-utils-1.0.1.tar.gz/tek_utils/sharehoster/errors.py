__copyright__ = """ Copyright (c) 2012-2013 Torsten Schmits

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

from tek.errors import MooException

class InvalidURLError(MooException):
    _text = 'Invalid sharehoster URL: {url}'

    def __init__(self, url, details=None):
        text = self._text.format(url=url)
        if details is not None:
            text = '{} ({})'.format(text, details)
        super(InvalidURLError, self).__init__(text)

class ShareHosterError(MooException):
    pass

class RapidshareError(ShareHosterError):
    pass

class IllegalFile(RapidshareError):

    def __init__(self, fname):
        text = 'DMCA takedown: {}'.format(fname)
        super(IllegalFile, self).__init__(text)

class NoMoreResults(MooException):
    def __init__(self):
        super(NoMoreResults, self).__init__('No more results.')

class NetloadError(ShareHosterError):
    pass

__all__ = ['InvalidURLError', 'RapidshareError', 'IllegalFile',
           'NoMoreResults', 'NetloadError']
