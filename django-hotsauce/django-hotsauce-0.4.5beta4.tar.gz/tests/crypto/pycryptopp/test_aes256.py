#!/usr/bin/env python

# test_aes256.py - Test suite for encryption and decryption of Python
# objects using AES 256 and pycryptopp.
#
# Copyright (C) 2009 Etienne Robillard <erob@gthcfoundation.org>
# All rights reserved.
#
# This file is part of the notmm distribution.
# Please see http://gthc.org/projects/notmm/0.2.12/ for details.

import os
import uuid
import pickle
import logging

logger = logging.getLogger('sandbox.logging_conf')

try:
    from pycryptopp.cipher.aes import AES
    logger.debug("Pycryptopp library found")
except ImportError:
    raise ImportError("Please install the pycryptopp package.""")


from notmm.datastore.threadlocal import LocalStore

from test_support import unittest

BLOCKSIZE = 16
SECRET_KEY = '\xad\x9eY}v\x19D\x1c)6\xd5 a\t&=pq\xa8'
UUID = uuid.uuid5(uuid.NAMESPACE_DNS, SECRET_KEY)

def uuid2bytes(obj):
    if getattr(obj, 'bytes'):
        assert len(obj.bytes) == BLOCKSIZE
        return obj.bytes
    return None

class AES256TextStore(LocalStore):

    def __init__(self, masterkey="\x00"*BLOCKSIZE):
        self.masterkey = masterkey
        self.engine = AES(key=masterkey)

    def encrypt(self, pyobj):
        # create a pickle object for this string
        obj = pickle.dumps(pyobj)
        self._ciphertext = self.engine.process(obj)
        return self

    def decrypt(self, key):
        pyobj = AES(key=key).process(self._ciphertext)
        self.__dict__.update(pickle.loads(pyobj))
        self.initialized = True
        return self

    #def save(self, filename):
    #
    #    fileobj = open(filename, 'w')
    #    fileobj.write(self.ciphertext)
    #    fileobj.close()
    #    #print "data saved to %r" % os.path.realpath(filename)
    #    return self

class AES256TextStore_TestCase(unittest.TestCase):

    # To encrypt a object programmatically with AES 256 encryption: 
    # >>> storable = CipherTextStore(masterkey="\x00"*16)
    # >>> storable.encrypt(dict(DEBUG=True))
    #
    # For accessing its value:
    # >>> storable.decrypt("\x00"*16)
    # >>> storable.DEBUG   
    # True 
    
    def setUp(self):
        self.data = {'DEBUG': True,
                     'SECRET_KEY': SECRET_KEY}
        self.key = uuid2bytes(UUID)
        self.modname = os.environ.get('DJANGO_SETTINGS_MODULE')
        self.storable = AES256TextStore(masterkey=self.key)
        #self.filename = '/tmp/file.dat'

    def tearDown(self):
        #if os.path.exists(self.filename): 
        #    os.remove(self.filename)    
        self.storable = None

    def test_encrypt(self):
        # Encrypt python objects to ciphertext using AES 256 
        self.storable.encrypt(self.data)

    def test_decrypt(self):
        self.storable.encrypt(self.data)
        self.storable.decrypt(self.key)
        
        self.assertEqual(self.storable.DEBUG, True)
        self.assertEqual(self.storable.SECRET_KEY, SECRET_KEY)
        self.assertEqual(self.storable.count(), 2)

if __name__ == '__main__':
    unittest.main()
