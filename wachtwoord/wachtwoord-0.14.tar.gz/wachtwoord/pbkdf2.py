"""Module level functions and a class for hashing and verifying passwords using PBKDF2.

Copyright (c) 2008 by Ori Peleg
Copyright (c) 2010 by Guido Kollerie.
License: 2-clause BSD license, see LICENSE for more details.
"""

import hashlib
import hmac
from wachtwoord.utils import bytes_to_base64_str, base64_str_to_bytes, random_bytes
from functools import reduce
from itertools import starmap
from math import ceil
import operator

__all__ = ['Engine', 'hash_password', 'verify_password', 'pbkdf2']

HASHES = {'sha1': hashlib.sha1, 'sha224': hashlib.sha224,
          'sha384': hashlib.sha384, 'sha256': hashlib.sha256,
          'sha512': hashlib.sha512, 'md5': hashlib.md5}
DELIMITER = '$'
METHODS = ('pbkdf2',)
KEY_LENGTH = 64

def timing_independent_byte_cmp(b_left, b_right):
    """A timing independent byte string compare from http://rdist.root .org/2009/05/28/timing-attack-in-google-keyczar-library/

    Comparing two byte strings of equal length iterates over their full length to prevent leaking timing information.
    If the strings are not of equal length False is returned immediately.

    :param b_left: a value to be compared
    :type b_left: byte string
    :param b_right: a value to be compared
    :type b_right: byte string

    :returns: True if ``b_left`` and ``b_right`` are equals, False if otherwise
    :rtype: boolean
    """
    if len(b_left) != len(b_right):
        return False
    result = 0
    for l, r in zip(b_left, b_right):
        result |= l ^ r
    return result == 0


def pseudo_pbkdf2(b_password, b_salt, iterations, digestmod):
    """Hash a ``password`` according to the http://stackoverflow.com/questions/287517/encrypting-hashing-plain-text-passwords-in-database/287883#287883

    This function is called pseudo_pbkdf2 as it does NOT implement PBKDF2 correctly. The StackOverflow article has been
    updated to reflect this.

    :param b_password: clear text password
    :type b_password: byte string
    :param b_salt: salt value
    :type b_salt: byte string
    :param iterations: number of times hash function should be applied
    :type iterations: integer
    :param digestmod: hash function
    :type digestmod: :mod:`hashlib` hash object or string name

    :returns: hashed password
    :rtype: byte string
    """
    b_hashed_password = b_password
    for _ in range(iterations):
        b_hashed_password = hmac.new(b_salt, b_hashed_password,
                                     digestmod).digest()
    return b_hashed_password


def pbkdf2(b_password, b_salt, iterations, key_length, digestmod):
    """Hash a ``password`` according to the PBKDF2 specification as detailed in RFC2898

    :param b_password: clear text password
    :type b_password: byte string
    :param b_salt: salt value
    :type b_salt: byte string
    :param iterations: number of times thee hash function should be applied
    :type iterations: integer
    :param key_length: the length of the derived key (the hashed password, the return value)
    :type key_length: integer
    :param digestmod: hash function
    :type digestmod: :mod:`hashlib` hash object or string name

    :returns: hashed password
    :rtype: byte string
    """

    mac = hmac.new(b_password, None, digestmod)

    def prf(b_text, mac=mac):
        m = mac.copy()
        m.update(b_text)
        return m.digest()

    def bytes_xor(b_left, b_right):
        return bytes(starmap(operator.xor, zip(b_left, b_right)))

    l = ceil(key_length / mac.digest_size)
    dk = []
    for block_index in range(1, l + 1):
        us = [prf(b_salt + block_index.to_bytes(4, byteorder='big'))]
        for i in range(iterations - 1):
            us.append(prf(us[i]))
        dk.append(reduce(bytes_xor, us))
    return reduce(operator.add, dk)[:key_length]


def hash_password(password, digestmod=hashlib.sha512, iterations=10000,
                  salt_size=32):
    """Hash a ``password`` according to the PBKDF2 specification.

    Hash a ``password `` using ``digestmod`` as the hash function, together with
    ``salt`` as the salt value for ``iterations`` number of times. This
    process of generating an hash encoded password (or derived key) is
    known as Password Based Key Derivation (Function) or PBKDF2 for short.

    See also: http://en.wikipedia.org/wiki/PBKDF2

    The main difference between this module level function and the
    :meth:`Engine.hash` method is that the verification of a valid
    :mod:`hashlib` hash object/function name and the hashing happens in one go
    for the module level function. Whereas it is split between
    :class:`Engine` instantiation (verification) and :meth:`Engine.hash`
    (hashing) for the :meth:`Engine.hash` method. The splitting is mostly useful
    for hashing many passwords using the same hash function as the
    verification only happens once.

    :param password: clear text password to be hashed
    :type password: unicode string
    :param digestmod: hash function to use
    :type digestmod: :mod:`hashlib` hash object or hash function name
    :param iterations: number of time to apply the hash function
    :type iterations: integer
    :param salt_size: length of the randomly generated salt
    :type salt_size: integer

    :returns: hash encoded string
    :rtype: unicode string
    """
    return Engine(digestmod, iterations, salt_size).hash(password)


def verify_password(password, hash_encoded_password):
    """Verify a ``password ``against an hash encoded password.

    Given a password verify it against a given hash encoded password. The hash
    encoded password needs to follow a specific format. :func:`.hash_password`
    and :meth:`Engine.hash` generate hash encoded passwords that follow this
    format.

    :param password: clear text password to be verified
    :type password: unicode string
    :param hash_encoded_password: hashed encoded password in specific format
                                  (see below)
    :type hash_encoded_password: unicode string

    :returns: True if ``password`` matches ``hash_encoded_password``, else
              False
    :rtype: boolean

    :raises ValueError: if either the ``hash_encode_password`` is incorrectly
                        formatted or if the hash function specified in the
                        ``hash_encoded_password`` is unsupported.

    The supported hash encoded password formats are:

    ``digestmod$iterations$salt$hashed_password``
    ``method$digestmod$iterations$salt$hashed_password``

    * ``method`` - the method used to hash the password
    * ``digestmod`` -  the hash function used to hash the password
    * ``iterations`` - the number of times the hash function is applied to
       the combination of the ``salt`` and the ``(hashed_)password``
    * ``salt`` - a random generated string to be concatenated with the
      ``password`` before applying the hash function
    * ``hashed_password`` the result of applying the hash function ``digestmod``
      ``iterations`` number of times to the concatenation of ``salt`` and
      ``(hashed_)password``.

    if ``method`` is not specified pseudo pbkdf2 is assumed. Pseudo pbkdf2 is a simple iterative application of a
    hash function to a password and salt. This format is only supported for backward compatibility reasons.

    Both the ``salt`` and the ``hash_encoded_password`` are in base64 format.
    """

    err_incorrect_fmt = "Expected hash encoded password in format "\
                        "'method{0}digestmod{0}iterations{0}salt{0}hashed_password'. "\
                        "Got '{{0}}' instead.".format(DELIMITER)

    try:
        *method, digestmod, iterations, salt, hashed_password = hash_encoded_password.split(DELIMITER)
    except ValueError as e:
        raise ValueError(err_incorrect_fmt.format(hash_encoded_password)) from e
    if len(method) > 1 or (len(method) == 1 and method[0] not in METHODS):
        raise ValueError(err_incorrect_fmt.format(hash_encoded_password))
    if digestmod not in HASHES.keys():
        raise ValueError(
            "Unsupported hash algorithm '{0}' for hash encoded password '{1}'.".format(digestmod,
                                                                                       hash_encoded_password))
    iter = int(iterations)
    b_salt = base64_str_to_bytes(salt)
    b_hashed_password = base64_str_to_bytes(hashed_password)
    b_password = password.encode()
    if len(method) == 0:
        # backward compatibility
        return timing_independent_byte_cmp(b_hashed_password, pseudo_pbkdf2(b_password, b_salt, iter,
                                                                            HASHES[digestmod]))
    elif method[0] == 'pbkdf2':
        return timing_independent_byte_cmp(b_hashed_password, pbkdf2(b_password, b_salt, iter, KEY_LENGTH,
                                                                     HASHES[digestmod]))
    else:
        raise Exception("Unexpected hashing method '{0}'".format(method[0]))


class Engine(object):
    """Captures settings for generating password hashes according to the PBKDF2
       specification.

    See also: http://en.wikipedia.org/wiki/PBKDF2

    If multiple password hashes need to be generated instantiating a
    :class:`Engine` object that captures the shared settings is slightly more
    convenient than using the module level function :func:`.hash_password` as
    initialization and verification is done only once.
    """

    def __init__(self, digestmod=hashlib.sha512, iterations=10000, salt_size=32):
        """Instantiate an Engine object that captures settings for generating
           password hashes.

        :param digestmod: hash function to use
        :type digestmod: :mod:`hashlib` hash object or function name
        :param iterations: number of times to apply the hash function
        :type iterations: integer
        :param salt_size: length of the randomly generated salt
        :type salt_size: integer

        :raises ValueError: if the ``digestmod`` is not an :mod:`hashlib` hash
                            object or hash function name.
        """
        if hasattr(digestmod, '__call__'):
            self.digestmod = digestmod
        elif digestmod in HASHES.keys():
            self.digestmod = HASHES[digestmod]
        else:
            raise ValueError(
                "Expected argument 'digestmod' needs to be one of the hash objects from hashlib or hashlib function name ({0}).".format(
                    ", ".join(HASHES.keys())))
        self.iterations = iterations
        self.salt_size = salt_size

    def hash(self, password):
        """Hash a ``password`` according to the PBKDF2 specification.

        Hash a ``password`` using the parameters specified in the
        :class:`Engine`` constructor.

        See also: :func:`.hash_password`

        :param password: clear text password to be hashed
        :type password: unicode string

        :returns: hash encoded string
        :rtype: unicode string
        """
        b_salt = random_bytes(self.salt_size)
        b_password = password.encode()
        b_hashed_password = pbkdf2(b_password, b_salt, self.iterations, KEY_LENGTH, self.digestmod)
        digestmod = self.digestmod.__name__.replace('openssl_', '')
        return METHODS[0] + DELIMITER + digestmod + DELIMITER + str(self.iterations) + DELIMITER + bytes_to_base64_str(
            b_salt) + DELIMITER + bytes_to_base64_str(b_hashed_password)

    def verify(self, password, hash_encoded_password):
        """Verify a password against an hash encoded password.

        See also: :func:`.verify_password`
        """
        return verify_password(password, hash_encoded_password)
