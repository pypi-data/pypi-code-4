#
# A Last.fm API interface.
# Copyright (C) 2013  Никола "hauzer" Вукосављевић
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#


"""
Holds :py:class:`Package`.

"""


class Package:
    """
    The base class for all :py:mod:`~lfm.packages`.
    
    :param app:
        The application whose :py:func:`~lfm.app.App.request` or :py:func:`~lfm.app.App.request_auto`
        will be called by all methods inside the package.
    
    :type app:
        :py:class:`~lfm.app.App`
    
    """
    
    app = None
    """ The associated :py:class:`~lfm.app.App`. """
    
    def __init__(self, app):
        self.app = app
        