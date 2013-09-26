__all__ = ['get_random_bytes', 'gen_token', 'hmac', 'sha256', 'AES']

from base64 import b64encode, b64decode
from hashlib import md5, sha256
import hmac as _hmac
from Crypto.Cipher import AES as _AES
from Crypto.Random import get_random_bytes

def gen_token(size = 32):
    try:
        return b64encode(get_random_bytes(size))
    except AssertionError:
        from Crypto import Random
        Random.atfork()
        return gen_token(size)

def hardened_key(key, hfun = sha256):
    return b64encode(hfun(hfun(key).digest()).digest())

def hmac(secret, text):
    return b64encode(_hmac.new(hardened_key(secret), text).digest())

def EVP_ByteToKey(password, salt, key_len=32, iv_len=16, df=md5):
    """
    Derive the key and the IV from the given password and salt.

    borrowed from
    http://stackoverflow.com/questions/13907841/implement-openssl-aes-encryption-in-python
    """
    dtot = df(password + salt).digest()
    d = [dtot]
    s_len = key_len + iv_len
    while len(dtot) < s_len:
        d.append(df(d[-1] + password + salt).digest())
        dtot += d[-1]
    return dtot[:key_len], dtot[key_len:s_len]

class AES(object):
    """
    OpenSSL compatible AES implementation.

    Interoperable with Crypto-JS
    https://code.google.com/p/crypto-js/#With_OpenSSL
    """

    def __init__(self, password, df=md5, mode=_AES.MODE_CBC):
        self.__password = hardened_key(password)
        self.__mode = mode
        self.__df = df

    def encrypt(self, text):
        salt = get_random_bytes(8)
        key, iv = EVP_ByteToKey(self.__password, salt, df=self.__df)
        l_pad = 16 - (len(text) % 16)
        t_pad = text + (chr(l_pad) * l_pad)
        cipher = _AES.new(key, self.__mode, iv)
        return b64encode('Salted__' + salt + cipher.encrypt(t_pad))

    def decrypt(self, enc):
        stream = b64decode(enc)
        assert stream[:8] == 'Salted__', 'Bad format'
        salt = stream[8:16]
        key, iv = EVP_ByteToKey(self.__password, salt, df=self.__df)
        cipher = _AES.new(key, self.__mode, iv)
        t_pad = cipher.decrypt(stream[16:])
        return t_pad[:-ord(t_pad[-1])]

def main():
    from sys import argv
    aes = AES(argv[-2])
    msg = argv[-1]
    enc = aes.encrypt(msg)
    assert msg == aes.decrypt(enc), 'failed'
    print 'OK (%f kb -> %f kb)' % (len(msg)/1024.0, len(enc)/1024.0)

if __name__ == '__main__':
    main()
