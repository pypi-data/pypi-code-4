# python-boxcar
#
# Copyright (C) 2013 Mark Caudill
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


class BoxcarError(Exception):
    '''Base Boxcar exception class.'''
    def __init__(self, value=None):
        self.value = value

    def __str__(self):
        return repr(self.value)


class UserNotSubscribed(BoxcarError):
    '''Raised when the user is not currently subscribed to this service.'''
    pass


class UserAlreadySubscribed(BoxcarError):
    '''Raised when the user is already subscribed to this service.'''
    pass


class UserDoesNotExist(BoxcarError):
    '''Raised when the user is not registerd on Boxcar.io.'''
    pass
