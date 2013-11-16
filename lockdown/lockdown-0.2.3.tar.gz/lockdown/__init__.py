''' lockdown
Tool for locking down Python source with AES-256.
'''

import sys
import os
import struct
import tarfile
from StringIO import StringIO
from getpass import getpass
from Crypto.Cipher import AES
from Crypto.Hash import SHA256
from Crypto import Random

class Lockdown(object):
    ''' Executes encrypted Python source and loads it into the namespace
    of the Lockdown instance
    '''

    def __init__(self, vault=None, key=None):
        ''' Creates a Lockdown instance.
        If vault is passed, it will use that when [un]locking.
        '''
        self.___glob = {}
        self.___vault = vault
        self.___ctr = None
        self.___key = key
        self.___cipher = None

    def _lockdown_load(self, path, name=None):
        ''' Loads a script into the namespace '''
        if name is None:
            name = os.path.basename(path)
            if name.endswith('.py'):
                name = name[:-3]
            name.replace('-', '_')
        module_d = {}
        execfile(path, module_d)
        self.___glob[name] = LockdownModule(name, module_d)

    def _lockdown_setup_cipher(self, iv=None):
        ''' Sets up an AES256 cipher in CTR mode.
        Gets a key from a password if key isn't initialized yet.
        '''
        if self.___key is None:
            self._lockdown_input_pass()
        self.___ctr = Counter(nonce=iv)
        self.___cipher = AES.new(
            self.___key, 
            AES.MODE_CTR, 
            counter=self.___ctr.counter
        )
    
    def _lockdown_input_pass(self, repeat=False):
        ''' Input a password and SHA256 it. '''
        if repeat:
            password = getpass()
            print >>sys.stderr, 'Enter again.'
            password2 = getpass()
            if password != password2:
                raise ValueError('Passwords didn\'t match.')
        else:
            password = getpass()
        self.___key = SHA256.new(password).digest()

    def __getattr__(self, attr):
        ''' Return the attribute of the namespace or None '''
        return self.___glob.get(attr)
        
    def _lockdown_encrypt_file(self, input_path):
        ''' Encrypts at the file path.
        Gets a cipher if has None, and resets it after.
        Returns the ciphertext.
        '''
        if self.___cipher is None:
            self._lockdown_setup_cipher()
        iv = self.___ctr.nonce
        with open(input_path) as input_f:
            plain = input_f.read()
        ctext = iv + self.___cipher.encrypt(plain)
        self.___cipher = None
        return ctext

    def _lockdown_decrypt_file(self, input_path):
        ''' Decrypts at the file path.
        Gets a cipher if has None, and resets it after.
        Returns the plaintext.
        '''
        with open(input_path) as input_f:
            ftext = input_f.read()
        iv = ftext[:8]
        ctext = ftext[8:]
        self._lockdown_setup_cipher(iv=iv)
        ptext = self.___cipher.decrypt(ctext)
        self.___cipher = None
        return ptext

    def lock(self, files, vault=None):
        ''' Lock files into a vault file '''
        if vault is None:
            vault = self.___vault
        # Nothing to lock?
        if vault is None:
            return
        tfile = tarfile.open(name=vault+'.tar.gz', mode='w:gz')
        for fil in files:
            tfile.add(fil)
        tfile.close()
        ctext = self._lockdown_encrypt_file(tfile.name)
        os.remove(tfile.name)
        with open(vault, 'w+') as vault_f:
            vault_f.write(ctext)
    
    def unlock(self, vault=None, delete=True):
        ''' Unlock a lockdown vault file '''
        if vault is None:
            vault = self.___vault
        # Nothing to unlock?
        if vault is None:
            return
        ptext = self._lockdown_decrypt_file(vault)
        try:
            tfile = tarfile.open(fileobj=StringIO(ptext))
        except tarfile.ReadError:
            self.___key = None
            raise ValueError('Bad password.')
        tfile.extractall()
        for member in tfile.getmembers():
            if member.isdir():
                continue
            self._lockdown_load(member.name)
        if delete:
            for member in tfile.getmembers():
                if member.isdir():
                    continue
                os.remove(member.name)
            

class LockdownModule(object):
    ''' Holds a module in a dict, and returns values with getattr '''
    def __init__(self, name, module_d):
        self.name = name
        self.module_d = module_d

    def __getattr__(self, attr):
        if attr in self.module_d:
            return self.module_d[attr]
        raise KeyError('Attribute not contained in ' + self.name)


class Counter(object):
    ''' Stateful counter for CTR mode of operation '''

    def __init__(self, nonce=None):
        self.ctr = 0
        if nonce is None:
            rand = Random.new()
            self.nonce = rand.read(8)
        else:
            self.nonce = nonce

    def counter(self):
        self.ctr += 1
        ctr = struct.pack('Q', self.ctr)
        return self.nonce + ctr

    def reset(self):
        self.ctr = 0

