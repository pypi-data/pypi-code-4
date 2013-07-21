#!/usr/bin/python
#  Copyright 2007 Olivier Grisel <olivier.grisel@ensta.org>
#
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""Utility script to build a set of strong yet rebuildable passwords

:author: Olivier Grisel <olivier.grisel@ensta.org>

The final password is build from a potentialy weak but easy to remember yet
secret master password and a domain-specific key like the name of the website
you are building a password for.

The password is then the 8th first characters of the letters + digits encoding
of sha1 digest of the concatenation of the master password and the domain key::

  >>> make_password("myprecious", "paypal")
  'muvcEizM'

  >>> make_password("myprecious", "jdoe@example.com", uppercase=False,
  ...               length=6)
  'ykn0nu'

  >>> make_password("myprecious", "jdoe@example.com", digits=False, length=10)
  'bdnrAGgJqe'

"""
from __future__ import print_function

import subprocess
import optparse
import pexpect
import socket
import string
import sys
import os
from time import sleep
from itertools import izip
from getpass import getpass

try:
    from hashlib import sha1
except ImportError:
    from sha import new as sha1

try:
    import xerox as clipboard
except ImportError:
    clipboard = None


ONE_BYTE = 2 ** 8
DEFAULT_LENGTH = 8  # default password length
DEFAULT_ALPHABET = string.lowercase + string.uppercase + string.digits


def bytes2number(bs):
    """Convert a python string (of bytes) into a python integer

    >>> bytes2number('0')
    48
    >>> bytes2number('00')
    12336
    >>> bytes2number('a0')
    24880

    """
    n = 0
    for i, c in izip(xrange(len(bs)), reversed(bs)):
        n += ord(c) * (ONE_BYTE ** i)
    return n


def number2string(n, alphabet='01'):
    """Compute the string representation of ``n`` in letters in ``alphabet``

    >>> number2string(0)
    '0'
    >>> number2string(1, '01')
    '1'
    >>> number2string(2, '01')
    '10'
    >>> number2string(3)
    '11'
    >>> number2string(4, '01')
    '100'

    >>> number2string(58, string.digits + 'abcdef')
    '3a'

    >>> number2string(-1, '01') #doctest: +ELLIPSIS
    Traceback (most recent call last):
    ...
    ValueError: -1 is not a natural number

    """
    base = len(alphabet)
    if n == 0:
        return alphabet[n]
    elif n < 0:
        raise ValueError("%d is not a natural number" % n)
    acc = []
    while n != 0:
        n, remainder = divmod(n, base)
        acc.append(alphabet[remainder])
    return ''.join(reversed(acc))


def bytes2string(bs, alphabet):
    """Transcode a string of bytes into an arbitrary alphabet"""
    return number2string(bytes2number(bs), alphabet)


def make_password(master_password, domain_key, lowercase=True, uppercase=True,
                  digits=True, length=DEFAULT_LENGTH, alphabet=None):
    """Build a password out of a master key and a domain key"""

    # build the sha1 hash of the concatenation of the keys
    hash = sha1(master_password + domain_key).digest()

    if alphabet is None:
        # determine the list of acceptable characters
        alphabet = ''
        alphabet += lowercase and string.lowercase or ''
        alphabet += uppercase and string.uppercase or ''
        alphabet += digits and string.digits or ''

    if not alphabet:
        raise ValueError('empty alphabet')

    # re-write the hash in the given alphabet and take the first chars as
    # final password
    return bytes2string(hash, alphabet)[:length]


def get_password(domain_key=None, lowercase=True, uppercase=True,
                 digits=True, length=DEFAULT_LENGTH, alphabet=None):
    """Prompt for master password and domain key. Return a password"""
    # password and domain prefix (if None) are read interactively from stdin to
    # avoid password data to be stored in the shell command history
    master_password = getpass("master password: ")
    if domain_key is None:
        domain_key = raw_input("domain key [e.g. 'login@host']: ")
    return make_password(master_password, domain_key,
                         uppercase=uppercase, digits=digits,
                         length=length, alphabet=alphabet)


def add_key():
    """print key and launch ssh-add
    """
    filename = os.path.expanduser('~/.virtualkeyring')
    if os.path.isfile(filename):
        host = open(filename).read()
        host = host.strip()
    else:
        host = socket.gethostname()
    try:
        passwd = get_password(host, length=20)
        child = pexpect.spawn('ssh-add')
        if child.expect('Enter passphrase for .*: ', timeout=3) == 0:
            child.sendline(passwd)
            if child.expect(pexpect.EOF, timeout=3) == 0:
                subprocess.call(['ssh-add', '-l'])
    except KeyboardInterrupt:
        pass


def parse_args(args):
    usage = "vkr -l 10 -a abcdefghijklmnopqrstuvwyz0123456789"
    parser = optparse.OptionParser(usage=usage)

    parser.add_option('-l', '--length',
                      dest='length',
                      default=DEFAULT_LENGTH,
                      type="int",
                      help=("Lenght of the generated password (default: %d)" %
                            DEFAULT_LENGTH))

    parser.add_option('-a', '--alphabet',
                      dest='alphabet',
                      default=DEFAULT_ALPHABET,
                      help=("Characters to be used for the generated password"
                            " (default: %s)" % DEFAULT_ALPHABET))

    parser.add_option('-o', '--stdout',
                      action="store_true",
                      dest='stdout',
                      default=False,
                      help="Display the password to stdout")

    return parser.parse_args(args=args)


def main():
    options, _ = parse_args(sys.argv)

    use_clipboard = clipboard is not None and not options.stdout

    if use_clipboard:
        original_clipboard_content = clipboard.paste()
    try:
        passwd = get_password(length=options.length,
                              alphabet=options.alphabet)
        if clipboard is None or options.stdout:
            print(passwd)
        else:
            clipboard.copy(passwd)
            print("Your password is available in the clipboard."
                  " You have 10s to paste it.")
            for i in range(10):
                sleep(1)
    except KeyboardInterrupt:
        pass
    finally:
        if use_clipboard and original_clipboard_content:
            print("Restauring original clipboard content.")
            clipboard.copy(original_clipboard_content)

if __name__ == "__main__":
    main()
