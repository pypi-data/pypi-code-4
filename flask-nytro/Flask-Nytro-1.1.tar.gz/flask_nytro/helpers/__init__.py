#Module for general helpers

import re, random, string
from unicodedata import normalize

def keygen(size=16, chars=string.letters+string.digits+'!@#$()_+-='):
    '''generates random key given a size'''
    return ''.join([ random.choice(chars) for i in xrange(size) ])

def slugify(string):
    '''creates a slug from a string'''
    if isinstance(string, str):
        string = string.decode('u8')
    string = normalize('NFKD', unicode(string.lower())).encode('ascii', errors='ignore')
    return re.sub('\W', '', re.sub('\s', '_', string)).replace('_', '-')