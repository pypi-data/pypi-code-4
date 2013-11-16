from getpass import getpass
from Crypto.Cipher import AES
from Crypto.Hash import SHA256
from lockdown import Lockdown

def lockdown():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('vault', help='Destination of encrypted archive')
    parser.add_argument('files', nargs='+', help='Files to encrypt')
    args = parser.parse_args()
    locker = Lockdown()
    locker._lockdown_input_pass(repeat=True)
    locker.lock(args.files, vault=args.vault)
    
