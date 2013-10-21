
""" ``padding`` module.

    see http://www.di-mgt.com.au/cryptopad.html
"""

from wheezy.security.crypto.comp import chr
from wheezy.security.crypto.comp import ord


def pad(s, block_size):
    """ Pad with zeros except make the last byte equal to the
        number of padding bytes.

        The convention with this method is usually always to
        add a padding string, even if the original plaintext was
        already an exact multiple of `block_size` bytes.

        ``s`` - byte string.
    """
    n = len(s) % block_size
    if n > 0:
        n = block_size - n
    else:
        n = block_size
    return (chr(0) * (n - 1)).join((s, chr(n)))


def unpad(s, block_size):
    """ Strip right by the last byte number.

        ``s`` - byte string.
    """
    n = len(s)
    if n == 0:
        return None
    n = n % block_size
    if n > 0:
        return None
    n = ord(s[-1])
    if n > block_size:
        return None
    return s[:-n]
