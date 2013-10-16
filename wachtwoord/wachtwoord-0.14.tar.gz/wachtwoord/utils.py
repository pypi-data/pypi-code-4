"""Utility functions for converting byte and unicode strings to and from
   base64 unicode strings.

Copyright (c) 2010 by Guido Kollerie.
License: 2-clause BSD license, see LICENSE for more details.
"""

__all__ = ['random_bytes', 'str_to_base64_str', 'bytes_to_base64_str',
           'base64_str_to_str', 'base64_str_to_bytes']

import base64
import os

def random_bytes(num_bytes):
    """Generate a byte string of specified length consisting of random byte
       characters.

    :param num_bytes: number of bytes/characters to be randomly generated
    :type num_bytes: integer

    :returns: random byte string
    :rtype: byte string
    """
    return os.urandom(num_bytes)


def str_to_base64_str(str):
    r"""Encode a unicode string as a base64 encoded unicode string.

    Encode a unicode string ``str`` to a base64 encoded unicode string without
    any leading or trailing whitespace (most notable without a trailing ``\n``
    character as most base64 encoding functions tend to append to the output).

    :param str: string to be base64 encoded
    :type str: unicode string

    :returns: base64 encoded unicode string
    :rtype: unicode string
    """
    return base64.b64encode(str.encode()).decode().strip()


def bytes_to_base64_str(b_str):
    r"""Encode a byte string as a base64 encoded unicode string.

    Encode a byte string ``b_str`` to a base64 encoded unicode string without any
    leading or trailing whitespace (most notable without a trailing ``\n``
    character as most base64 encoding functions tend to append to the output).

    :param b_str: byte string to be base64 encoded
    :type b_str: byte string

    :returns: base64 encoded unicode string
    :rtype: unicode string

    """
    return base64.b64encode(b_str).decode().strip()


def base64_str_to_str(str):
    r"""Decode a base64 encoded unicode string as a unicode string.

    :param str: base64 encoded unicode string to be decoded
    :type str: unicode string

    :returns: decoded unicode string
    :rtype: unicode string
    """
    return base64.b64decode(str.encode()).decode()


def base64_str_to_bytes(str):
    r"""Decode a base64 encoded unicode string as a byte string.

    :param str: base64 encoded unicode string to be decoded
    :type str: unicode string

    :returns: decoded unicode string
    :rtype: unicode string
    """
    return base64.b64decode(str.encode())