
""" ``comp`` module.
"""

import sys

from warnings import warn


PY3 = sys.version_info[0] >= 3

if PY3:  # pragma: nocover
    bytes_type = bytes
    str_type = str
    chr = lambda i: bytes((i,))
    ord = lambda b: b

    def n(s, encoding='latin1'):
        if isinstance(s, str_type):
            return s
        return s.decode(encoding)

    def btos(b, encoding):
        return b.decode(encoding)

    u = lambda s: s

else:  # pragma: nocover
    bytes_type = str
    str_type = unicode
    chr = chr
    ord = ord

    def n(s, encoding='latin1'):  # noqa
        if isinstance(s, bytes_type):
            return s
        return s.encode(encoding)

    def btos(b, encoding):  # noqa
        return b.decode(encoding)

    u = lambda s: unicode(s, 'unicode_escape')


def b(s, encoding='latin1'):  # pragma: nocover
    if isinstance(s, bytes_type):
        return s
    return s.encode(encoding)


# Hash functions
try:  # pragma: nocover
    # Python 2.5+
    from hashlib import md5, sha1, sha224, sha256, sha384, sha512
    digest_size = lambda d: d().digest_size

    try:
        from hashlib import new as openssl_hash
        ripemd160 = lambda: openssl_hash('ripemd160')
        whirlpool = lambda: openssl_hash('whirlpool')
    except ValueError:
        ripemd160 = None
        whirlpool = None
except ImportError:  # pragma: nocover
    import md5  # noqa
    import sha as sha1  # noqa
    sha224 = sha256 = sha384 = sha512 = ripemd160 = whirlpool = None  # noqa
    digest_size = lambda d: d.digest_size

# Encryption interface
block_size = None
encrypt = None
decrypt = None

# Supported cyphers
aes128 = None
aes192 = None
aes256 = None
aes128iv = None
aes192iv = None
aes256iv = None

# Python Cryptography Toolkit (pycrypto)
try:  # pragma: nocover
    from Crypto.Cipher import AES
    from Crypto.Random import get_random_bytes

    # pycrypto interface
    block_size = lambda c: c.block_size
    encrypt = lambda c, v: c.encrypt(v)
    decrypt = lambda c, v: c.decrypt(v)

    class AESIVCipher(object):
        """ AES cipher that uses random IV for each encrypt operation
            and prepend it to cipher text; decrypt splits input value into
            IV and cipher text.
        """
        block_size = 16

        def __init__(self, key):
            self.key = key

        def encrypt(self, v):
            iv = get_random_bytes(16)
            c = AES.new(self.key, AES.MODE_CBC, iv)
            return iv + c.encrypt(v)

        def decrypt(self, v):
            c = AES.new(self.key, AES.MODE_CBC, v[:16])
            return c.decrypt(v[16:])

    # suppored cyphers
    def aes(key, key_size=32):
        assert len(key) >= key_size
        if len(key) < key_size + 16:
            warn('AES%d: key and iv overlap.' % (key_size * 8))
        key = key[-key_size:]
        iv = key[:16]
        return lambda: AES.new(key, AES.MODE_CBC, iv)

    def aesiv(key, key_size=32):
        assert len(key) >= key_size
        c = AESIVCipher(key[:key_size])
        return lambda: c

    aes128 = lambda key: aes(key, 16)
    aes192 = lambda key: aes(key, 24)
    aes256 = lambda key: aes(key, 32)
    aes128iv = lambda key: aesiv(key, 16)
    aes192iv = lambda key: aesiv(key, 24)
    aes256iv = lambda key: aesiv(key, 32)
except ImportError:  # pragma: nocover
    # TODO: add fallback to other encryption providers
    pass
