# -*- coding: utf-8 -*-

# Copyright 2013, Bert Vanderbauwhede
#
# This file is part of fnord.easycodec.
#
# fnord.easycodec is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# fnord.easycodec is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY
# or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU Lesser General Public
# License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with fnord.easycodec.  If not, see <http://www.gnu.org/licenses/>.

import sys

if sys.version >= "2.5":
    from functools import wraps
else:
    wraps = lambda func: func


def encoder(encoding):
    """Decorator for an encoder.
    """
    def func_wrapper(func):
        @wraps(func)
        def wrapper(string, errors="strict"):
            if errors != "strict":
                raise UnicodeError(
                    u"Unsupported error handling: %s" % errors)

            try:
                return func(string), len(string)
            except:
                raise UnicodeEncodeError(
                    encoding, u"", 0, len(string), "Can't encode string")

        return wrapper

    return func_wrapper


def decoder(encoding):
    """Decorator for a decoder.
    """
    def func_wrapper(func):
        @wraps(func)
        def wrapper(string, errors="strict"):
            if errors != "strict":
                raise UnicodeError(
                    u"Unsupported error handling: %s" % errors)

            try:
                return func(string), len(string)
            except:
                raise UnicodeDecodeError(
                    encoding, u"", 0, len(string), "Can't decode string")

        return wrapper

    return func_wrapper
