''' lockdown
Tool for locking down Python source with AES-256.
'''

import sys
import os
import struct
import tarfile
# For treating tar files in memory as an open file
from StringIO import StringIO
from getpass import getpass
from Crypto.Cipher import AES
from Crypto.Hash import HMAC
from Crypto.Protocol.KDF import PBKDF2
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
        self.___cipher = None
        self.___keys = { "HMAC": None, "AES": None }
        self.___salts = { "HMAC": None, "AES": None }

    def _lockdown_create_name(self, filename):
        name = os.path.basename(filename)
        if name.endswith('.py'):
            name = name[:-3]
        name.replace('-', '_')
        return name

    def _lockdown_load(self, fil, name):
        ''' Loads a script into the namespace given a path/fileobj and name.
        '''
        module_d = {}
        if isinstance(fil, basestring):
            execfile(fil, module_d)
        else:
            exec(fil.read(), module_d)
        self.___glob[name] = LockdownModule(name, module_d)

    def _lockdown_setup_cipher(self, salts=None, iv=None):
        ''' Sets up an AES256 cipher in CTR mode.
        Gets a key from a password if key isn't initialized yet.
        '''
        if self.___keys['AES'] is None:
            self._lockdown_input_pass(salts=salts)
        self.___ctr = Counter(nonce=iv)
        self.___cipher = AES.new(
            self.___keys['AES'], 
            AES.MODE_CTR, 
            counter=self.___ctr.counter
        )
    
    def _lockdown_input_pass(self, salts=None, repeat=False):
        ''' Input a password and derive keys. '''
        if repeat:
            password = getpass()
            print >>sys.stderr, 'Enter again.'
            password2 = getpass()
            if password != password2:
                raise ValueError('Passwords didn\'t match.')
        else:
            password = getpass()
        rand = Random.new()
        if salts is None:
            self.___salts['AES'] = rand.read(8)
            self.___salts['HMAC'] = rand.read(8)
        else:
            self.___salts['AES'] = salts['AES']
            self.___salts['HMAC'] = salts['HMAC']
        self.___keys['AES'] = PBKDF2(self.___salts['AES'], password, dkLen=32)
        self.___keys['HMAC'] = PBKDF2(self.___salts['HMAC'], password, 
            dkLen=32)

    def __getattr__(self, attr):
        ''' Return the attribute of the namespace or None '''
        return self.___glob[attr]
        
    def _lockdown_gen_hmac(self, ctext, iv):
        ''' Generate an HMAC from cipher text and its IV '''
        hmac = HMAC.new(self.___keys['HMAC'])
        hmac.update(iv + ctext)
        # Returns 16 bytes by default.
        return hmac.digest()

    def _lockdown_breakout_prefix(self, prefix):
        ''' Break out the parts of data from the prefix, should be 40 bytes.
        8 bytes HMAC salt, 16 bytes HMAC, 8 bytes AES salt, 8 bytes IV.
        '''
        self.___salts['HMAC'] = prefix[:8]
        hmac = prefix[8:24]
        self.___salts['AES'] = prefix[24:32]
        iv = prefix[32:40]
        return (hmac, iv)
        
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
        ctext = self.___cipher.encrypt(plain)
        self.___cipher = None
        hmac = self._lockdown_gen_hmac(ctext, iv)
        # 8 byte HMAC salt + 16 byte HMAC + 8 byte AES salt + 8 byte IV
        prefix = self.___salts['HMAC'] + hmac + self.___salts['AES'] + iv
        return prefix + ctext

    def _lockdown_decrypt_file(self, input_path):
        ''' Decrypts at the file path.
        Gets a cipher if has None, and resets it after.
        Returns the plaintext.
        '''
        with open(input_path) as input_f:
            ftext = input_f.read()
        # Side effects: self.___salts are set up now from the prefix.
        hmac, iv = self._lockdown_breakout_prefix(ftext)
        ctext = ftext[40:]
        self._lockdown_setup_cipher(salts=self.___salts, iv=iv)
        ptext = self.___cipher.decrypt(ctext)
        hmac_digest = self._lockdown_gen_hmac(ctext, iv)
        if hmac_digest != hmac:
            raise ValueError('HMAC didnt match.\n'
                'Someone could be doing something nasty.')
        self.___cipher = None
        return ptext

    def lock(self, files, vault=None, delete=False):
        ''' Lock files into a vault file
        Set delete=True if you want to delete the files you pass in.
        '''
        if vault is None:
            vault = self.___vault
        # Nothing to lock?
        if vault is None:
            raise ValueError('No vault to lock.')
        tfile = tarfile.open(name=vault+'.tar.gz', mode='w:gz')
        for fil in files:
            tfile.add(fil)
            if delete: 
                os.remove(fil)
        tfile.close()
        ctext = self._lockdown_encrypt_file(tfile.name)
        os.remove(tfile.name)
        with open(vault, 'w+') as vault_f:
            vault_f.write(ctext)
    
    def unlock(self, vault=None, load_in_memory=True, delete=True):
        ''' Unlock a lockdown vault file
        load_in_memory will execute the files in memory one at a time, instead
        of using extractall. I believe this is safer than writing to disk.
        The bad side to this is that you can't import from each other
        vaulted file. I'll leave the option to clear that flag, but I don't
        think it's a good idea.
        '''
        if vault is None:
            vault = self.___vault
        # Nothing to unlock?
        if vault is None:
            raise ValueError('No vault to unlock.')
        ptext = self._lockdown_decrypt_file(vault)
        try:
            tfile = tarfile.open(fileobj=StringIO(ptext))
        except tarfile.ReadError:
            self.___keys = { "HMAC": None, "AES": None, }
            raise ValueError('Bad password.')
        if not load_in_memory:
            tfile.extractall()
        for member in tfile.getmembers():
            if member.isdir(): continue
            if load_in_memory:
                member_f = tfile.extractfile(member)
            else:
                member_f = member.name
            name = self._lockdown_create_name(member.name)
            self._lockdown_load(member_f, name)
        if not load_in_memory and delete:
            for member in tfile.getmembers():
                if member.isdir(): continue
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

