# -*- coding: utf-8 -*-
# Copyright (c) 2001-2011 LOGILAB S.A. (Paris, FRANCE). All rights Reserved.
# http://www.logilab.fr/ -- mailto:contact@logilab.fr
"""
PyBill packaging information
"""
from os import path as osp


# package name
modname = 'pybill'
debian_name = 'pybill'

# release version
numversion = (1, 1, 0)
version = '.'.join([str(num) for num in numversion])

pyversions = ['2.4','2.5', '2.6']

# license and copyright
license = "GPL"
copyright = """Copyright (c) 2001-2011 LOGILAB S.A. (Paris, FRANCE). All rights Reserved.
http://www.logilab.fr/ -- mailto:contact@logilab.fr"""

# short and long description
short_desc = "PDF formatting tool for bills"
try:
    long_desc = open(osp.join(osp.abspath(osp.dirname(__file__)), "README")).read()
except Exception, exc:
    long_desc = short_desc

# author name and email
author = "Olivier Cayrol"
author_email = "olivier.cayrol@logilab.fr"

# home page
web = "http://www.logilab.org/project/pybill"

# mailing list
mailinglist = 'mail-to://management-projects@lists.logilab.org' 

# download place
ftp = "ftp://ftp.logilab.org/pub/%s" % modname

# executable (include the 'bin' directory in the name)
scripts = ('bin/pybill',)

# should it be placed as a subpackage of a package such as 'logilab'
subpackage_of = None

# is there some directories to include with the source installation
include_dirs = []
