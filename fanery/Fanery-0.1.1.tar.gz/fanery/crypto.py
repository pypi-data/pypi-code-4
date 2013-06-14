__all__ = ['gen_token', 'digest', 'xor', 'encrypt', 'decrypt']

from numpy import frombuffer, bitwise_xor, byte
from base64 import b64encode, b64decode
from hashlib import sha256 as hashfun
from os import urandom as rand_bytes
from fanery.terms import is_string, to_json, parse_json

def gen_token(size = 32):
    return b64encode(rand_bytes(size))

def digest(term):
    return b64encode(hashfun(term if is_string(term) else str(term)).digest())

def xor(key, msg):
    key_buff = frombuffer(key, dtype = byte)
    msg_buff = frombuffer(msg, dtype = byte)
    return bitwise_xor(key_buff, msg_buff).tostring()

def cipher(key, msg):
    k = digest(key)
    klen = len(k)
    div, mod = divmod(len(msg), klen)
    for i in xrange(div):
        k = digest(k)
        yield xor(k, msg[i*klen:(i+1)*klen])
    if mod:
        k = digest(k)
        yield xor(k[:mod], msg[-mod:])

def encrypt(key, term):
    return b64encode(''.join(cipher(key, to_json(term))))

def decrypt(key, enc):
    return parse_json(''.join(cipher(key, b64decode(enc))))
