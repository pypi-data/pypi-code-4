#!/usr/bin/python
# -*- coding: utf-8 -*-

# This module is part of formv and is released under the MIT License: 
# http://www.opensource.org/licenses/mit-license.php 

import hmac 
from hashlib import sha256 
from base64 import b64encode 

from Crypto import Random
from Crypto.Protocol.KDF import PBKDF2

__all__ = ('crypt','decode','encode','sign',)

prf = lambda v, s: hmac.new(v, s, sha256).digest()

def crypt(value, salt=None, key_len=32, cost=2**12):  
    """  returns a string that contains (separated by $): 
            - algorithm, key length, cost, salt, hash
        - hash match is possible using embedded (key length, cost, salt)
        - default: salt = 128-bit (8x16); hash = 256-bit (8x32)
    """  
    salt = decode(salt or b64encode(Random.new().read(16), b'./'))    
    a = 'x-pbkdf2'; o = '$%(a)s$%(k)x$%(c)x$%(s)s$%(h)s'
    if salt.startswith('$'+a+'$'):
        (_, _, key_len, cost, salt, _) = salt.split('$')
        key_len = int(key_len, 16); cost = int(cost, 16)
    h = b64encode(PBKDF2(value, encode(salt), key_len, cost, prf), b'./')
    return o % dict(a=a, k=key_len, c=cost, s=salt, h=decode(h))


def sign(value, salt, key_len=32, cost=2**12):  
    return b64encode(PBKDF2(value, salt, key_len, cost, prf), b'./')


def encode(value):
    try:
        return value.encode('utf-8', 'strict')
    except AttributeError:
        return value


def decode(value):
    try:
        return value.decode('utf-8', 'strict')
    except AttributeError:
        return value