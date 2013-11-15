#!/usr/bin/python
# -*- coding: utf-8 -*-

# This module is part of formv and is released under the MIT License: 
# http://www.opensource.org/licenses/mit-license.php 

import sys
PY2 = sys.version_info[0] == 2
PY3 = sys.version_info[0] >= 3

if PY2:
    def iteritems(d):
        return d.iteritems()
    def itervalues(d):
        return d.itervalues()

if PY3:
    def iteritems(d):
        return d.items()
    def itervalues(d):
        return d.values()
    
if PY2:
    import urlparse
    from urllib2 import urlopen
    from urllib2 import URLError
if PY3:
    from urllib import parse as urlparse
    from urllib.request import urlopen
    from urllib.error import URLError