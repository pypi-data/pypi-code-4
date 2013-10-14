import string
import random
import hmac
import hashlib


PW_CHARS = string.ascii_letters + string.digits + string.punctuation
DEFAULT_LEN = 25


def bytes_to_pw(b):
    r'''
    encode bytes in a valid password string

    >>> bytes_to_pw(b'\xc0\xff\xee')
    'pvR+'
    '''
    n = int.from_bytes(b, byteorder='big')
    pw = ''
    while n > 0:
        pw += PW_CHARS[n % len(PW_CHARS)]
        n //= len(PW_CHARS)
    return ''.join(reversed(pw))


def gen_random(master_pw, entry, length=DEFAULT_LEN):
    return ''.join(random.choice(PW_CHARS) for _ in range(length))


def gen_hmac_sha512(master_pw, entry, length=DEFAULT_LEN):
    hm = hmac.new(master_pw, entry, hashlib.sha512).digest()
    return bytes_to_pw(hm)[:length]


ALGORITHMS = {
    'random': gen_random,
    'hmac_sha512': gen_hmac_sha512,
}
