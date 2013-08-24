# -*- coding: utf-8 -*-
#
# src/configviper/converters.py
# https://bitbucket.org/danielgoncalves/configviper
#
# ConfigViper  Copyright (C) 2012  Daniel Gonçalves <daniel@base4.com.br>
#
# This file is part of ConfigViper.
#
# ConfigViper is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as 
# published by the Free Software Foundation, either version 3 of the 
# License, or (at your option) any later version.
#
# ConfigViper is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with ConfigViper. If not, see <http://www.gnu.org/licenses/>.
#

import datetime
import decimal

class Converter(object):
    """Base class for configuration value converters."""

    def __init__(self):
        super(Converter, self).__init__()
        
    def to_json(self, value):        
        """Convert from Python data type to a type that JSON can handle."""
        return value
        
    def to_python(self, value):
        """Convert a JSON value to a Python data type."""
        return value


class DatetimeConverter(Converter):
    """A converter for ``datetime.datetime`` configuration value objects. When
    converted from Python, the result string will be formated as
    ``yyyy-mm-dd hh:MM:ss``.
    """
    
    def __init__(self):
        super(DatetimeConverter, self).__init__()

    def to_json(self, value):
        """Convert ``datetime.datetime`` objects to an understandable string
        representation.
        """
        return value.strftime('%Y-%m-%d %H:%M:%S')
        
    def to_python(self, value):
        """Convert a string to a ``datetime.datetime`` object, as if it's
        formatted like ``yyyy-mm-dd hh:MM:ss``.
        """
        return datetime.datetime.strptime(value, '%Y-%m-%d %H:%M:%S')


class DateConverter(Converter):
    """A converter for ``datetime.date`` configuration value objects. When
    converted from Python, the result string will be formated as ``yyyy-mm-dd``.
    """

    def __init__(self):
        super(DateConverter, self).__init__()

    def to_json(self, value):
        """Convert ``datetime.date`` objects to an understandable string
        representation.
        """
        return value.strftime('%Y-%m-%d')
        
    def to_python(self, value):
        """Convert a string to a ``datetime.date`` object, as if it's formatted
        like ``yyyy-mm-dd``.
        """
        return datetime.datetime.strptime(value, '%Y-%m-%d').date()
        
        
class TimeConverter(Converter):
    """A converter for ``datetime.time`` configuration value objects. When
    converted from Python, the result string will be formated as ``hh:MM:ss``.
    """

    def __init__(self):
        super(TimeConverter, self).__init__()

    def to_json(self, value):
        """Convert ``datetime.time`` objects to an understandable string
        representation.
        """
        return value.strftime('%H:%M:%S')
        
    def to_python(self, value):
        """Convert a string to a ``datetime.time`` object, as if it's formatted
        like ``hh:MM:ss``.
        """
        return datetime.datetime.strptime(value, '%H:%M:%S').time()
        

class DecimalConverter(Converter):
    """A converter for ``decimal.Decimal`` configuration value objects. 
    This converter should be used for simple values that's expected to behave
    in a predictable manner, like money values, since this converter simple
    convert from Python using ``str`` and to Python using ``decimal.Decimal``
    constructor on a string value.
    """

    def __init__(self):
        super(DecimalConverter, self).__init__()

    def to_json(self, value):
        """Convert ``decimal.Decimal`` objects to a string representation."""
        return str(value)
        
    def to_python(self, value):
        """Convert a string to a ``decimal.Decimal`` object."""
        return decimal.Decimal(value)
       
        
DEFAULT_CONVERTER = Converter()
"""A :class:`~configviper.converters.Converter` instance."""


DATETIME_CONVERTER = DatetimeConverter()
"""A :class:`~configviper.converters.DatetimeConverter` instance."""


DATE_CONVERTER = DateConverter()
"""A :class:`~configviper.converters.DateConverter` instance."""


TIME_CONVERTER = TimeConverter()
"""A :class:`~configviper.converters.TimeConverter` instance."""


DECIMAL_CONVERTER = DecimalConverter()
"""A :class:`~configviper.converters.DecimalConverter` instance."""
