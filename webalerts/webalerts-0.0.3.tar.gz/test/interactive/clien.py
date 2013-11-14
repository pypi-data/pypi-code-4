#! /usr/bin/env python
from getpass import getpass
import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

from webalerts.sites.clien import ClienBrowser


def test_login():
    username = raw_input('Clien username: ')
    password = getpass('Clien password: ')
    site = ClienBrowser(username, password)
    site.login()
    print 'Logged in'


if __name__ == '__main__':
    test_login()
