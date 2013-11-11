#coding=utf-8

MM_DEFAULT_FROM = 'www-data <root@localhost>'
MM_DEFAULT_MAILER = 'RamenMTA'
MM_DEFAULT_CRLF = '\r\n'

from hashlib import md5
import time, random, base64


def chunk_split(source, size=76, separator = MM_DEFAULT_CRLF):
    return separator.join([source[i:i+size] for i in range(0, len(source), size)])

def encode_content(string):
    return chunk_split(base64.b64encode(string))

def gen_boundary_hash():
    return md5( '%d%f%d' % (random.randint(100000, 999999), time.time(), random.randint(0, 1000)) ).hexdigest()

def encode_header(string, charset = 'UTF-8'):
    return '=?' + charset + '?B?' + base64.b64encode(string) + '?='

class MimemailException(Exception):
    pass
