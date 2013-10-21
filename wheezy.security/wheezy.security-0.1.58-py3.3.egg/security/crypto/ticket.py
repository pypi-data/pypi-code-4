
""" ``crypto`` module.
"""

from base64 import b64decode
from base64 import b64encode
from binascii import Error as BinError
from hmac import new as hmac_new
from os import urandom
from struct import pack
from struct import unpack
from time import time
from warnings import warn

from wheezy.security.crypto.comp import aes128
from wheezy.security.crypto.comp import b
from wheezy.security.crypto.comp import block_size
from wheezy.security.crypto.comp import btos
from wheezy.security.crypto.comp import decrypt
from wheezy.security.crypto.comp import digest_size
from wheezy.security.crypto.comp import encrypt
from wheezy.security.crypto.comp import sha1
from wheezy.security.crypto.padding import pad
from wheezy.security.crypto.padding import unpad

BASE64_ALTCHARS = b('-~')
EMPTY = b('')
EPOCH = 1317212745


def ensure_strong_key(key, digestmod):
    """ Translates a given key to a computed strong key of length
        3 * digestmode.digest_size suitable for encryption, e.g.
        with digestmod set to ``sha1`` returns 480 bit (60 bytes) key.
    """
    hmac = hmac_new(key, key, digestmod)
    k1 = hmac.digest()
    hmac.update(k1)
    k2 = hmac.digest()
    hmac.update(k2)
    return k1 + k2 + hmac.digest()


def timestamp():
    return int(time()) - EPOCH


class Ticket(object):
    """ Protects sensitive information (e.g. user id).

        Default policy applies verification and encryption.
        Verification is provided by ``hmac`` initialized with ``sha1``
        digestmod. Encryption is provided if available, by default
        it attempts to use AES cypher.
    """
    __slots__ = ('cypher', 'max_age', 'hmac', 'digest_size', 'block_size')

    def __init__(self, max_age=900, salt='', digestmod=None,
                 cypher=aes128, options=None):
        self.max_age = max_age
        if not digestmod:
            warn('Ticket: digestmod is not specified, fallback to sha1',
                 stacklevel=2)
            digestmod = sha1
        options = options or {}
        key = b(salt + options.get('CRYPTO_VALIDATION_KEY', ''))
        key = ensure_strong_key(key, digestmod)
        self.hmac = hmac_new(key, digestmod=digestmod)
        self.digest_size = digest_size(digestmod)
        if cypher:
            key = b(salt + options.get('CRYPTO_ENCRYPTION_KEY', ''))
            key = ensure_strong_key(key, digestmod)
            self.cypher = cypher(key)
            self.block_size = block_size(self.cypher())
        else:
            self.cypher = None
            warn('Ticket: cypher not available', stacklevel=2)

    def encode(self, value, encoding='UTF-8'):
        """ Encode ``value`` according to ticket policy.
        """
        value = b(value, encoding)
        expires = pack('<i', timestamp() + self.max_age)
        noise = urandom(12)
        value = EMPTY.join((
            noise[:4],
            expires,
            noise[4:8],
            value,
            noise[8:]
        ))
        if self.cypher:
            value = encrypt(self.cypher(), pad(value, self.block_size))
        return btos(b64encode(self.sign(value) + value, BASE64_ALTCHARS),
                    'latin1')

    def decode(self, value, encoding='UTF-8'):
        """ Decode ``value`` according to ticket policy.
        """
        if len(value) < 48:
            return (None, None)
        try:
            value = b64decode(b(value), BASE64_ALTCHARS)
        except (TypeError, BinError):
            return (None, None)
        signature = value[:self.digest_size]
        value = value[self.digest_size:]
        if signature != self.sign(value):
            return (None, None)
        if self.cypher:
            if len(value) % self.block_size != 0:
                return (None, None)
            value = unpad(decrypt(self.cypher(), value), self.block_size)
            if value is None:
                return (None, None)
        if len(value) < 16:  # pragma: nocover
            return (None, None)
        expires, value = value[4:8], value[12:-4]
        time_left = unpack('<i', expires)[0] - timestamp()
        if time_left < 0 or time_left > self.max_age:
            return (None, None)
        try:
            return (btos(value, encoding), time_left)
        except UnicodeDecodeError:
            return (None, None)

    def sign(self, value):
        """ Compute hmac digest.
        """
        h = self.hmac.copy()
        h.update(value)
        return h.digest()
