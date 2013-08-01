##############################################################################
#
# Copyright (c) 2006 Zope Corporation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""Get a URL using urllib2.  Intended for manual testing of the sftp support

This script provides for crude manual testing of the sftp support
until I figure out how to do automated tests.

Usage: bin/py get.py url

You can give multiple urls.

$Id: get.py 70169 2006-09-14 11:11:38Z jim $
"""

import sys, urllib2, zc.buildoutsftp.buildoutsftp

zc.buildoutsftp.buildoutsftp.install(None)

for url in sys.argv[1:]:
    print '=' * 70
    print url
    print '=' * 70
    f = urllib2.urlopen(url)
    print f.url
    print f.geturl()
    print f.headers
    print f.info()
    
    print
    print f.read()

