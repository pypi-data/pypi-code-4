import os
from subprocess import Popen, PIPE


GPG_OPTS = ['-q', '--batch', '--no-tty']
ENCRYPT_OPTS = ['-e', '--armor', '--default-recipient-self']
DECRYPT_OPTS = ['-d']


class GpgError(IOError):
    pass


def gpg(gpg_args, stdin):
    '''Run gpg with gpg_args and stdin as input. Return the produced output.'''
    cmd = ['gpg'] + GPG_OPTS + gpg_args
    try:
        p = Popen(cmd, stdin=PIPE, stdout=PIPE)
    except OSError as e:
        raise GpgError(e)
    stdout, _ = p.communicate(stdin)
    if p.returncode:
        raise GpgError('gpg returned with exit code {}'.format(p.returncode))
    return stdout


def encrypt(plaintext):
    '''Encrypt plaintext for the default gpg key.'''
    return gpg(ENCRYPT_OPTS, plaintext)


def decrypt(ciphertext):
    '''Decrypt ciphertext with the default gpg key.'''
    return gpg(DECRYPT_OPTS, ciphertext)


class EncryptedFile:
    '''Transparently read from and write to an gpg encrypted file.'''
    ENCODING = 'utf-8'

    def __init__(self, filename):
        self.filename = os.path.expanduser(filename)

    def read(self):
        '''Return the decrypted content that is stored inside of the file.'''
        with open(self.filename, 'rb') as f:
            ciphertext = f.read()
        return decrypt(ciphertext).decode(self.ENCODING)

    def write(self, content):
        '''Write content to the file after encrypting it.'''
        encrypted = encrypt(content.encode(self.ENCODING))
        with open(self.filename, 'wb') as f:
            f.write(encrypted)
