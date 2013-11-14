#! /usr/bin/env python
from getpass import getpass
import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

from webalerts.sites.cgv import CGVBrowser

# import httplib
# httplib.HTTPConnection.debuglevel = 1

# import logging
# logging.basicConfig(level=logging.DEBUG)


def test_login():
    username = raw_input('CGV username: ')
    password = getpass('CGV password: ')
    site = CGVBrowser(username, password)
    site.login()
    print 'Logged in'


if __name__ == '__main__':
    test_login()
