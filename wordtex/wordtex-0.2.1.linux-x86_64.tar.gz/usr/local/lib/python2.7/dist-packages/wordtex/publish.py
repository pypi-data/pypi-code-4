#!/usr/bin/python
# -*- coding: utf-8 -*-
#     LICENSE: The GNU Public License v3 or Greater
#
#     WordTeX (wordtex) v0.2.1
#     Copyright 2013 Garrett Berg
#     
#     Loosly based on LaTeX2WP version 0.6.2, Luca Trevisan Copyright 2009
#    
#     This file is part of wordtex, a program that converts
#     a LaTeX document into a format that is ready to be
#     copied and pasted into WordPress.
#    
#     You are free to redistribute and/or modify wordtex under the
#     terms of the GNU General Public License (GPL), version 3
#     or (at your option) any later version.
#    
#     You should have received a copy of the GNU General Public
#     License along with wordtex.  If you can't find it,
#     see <http://www.gnu.org/licenses/>
import pdb
from cloudtb import publish

VERSION = '0.2.1'
publish.YOUR_LICENSE = """
#     LICENSE: The GNU Public License v3 or Greater
#
#     WordTeX (wordtex) v{version}
#     Copyright 2013 Garrett Berg
#     
#     Loosly based on LaTeX2WP version 0.6.2, Luca Trevisan Copyright 2009
#    
#     This file is part of wordtex, a program that converts
#     a LaTeX document into a format that is ready to be
#     copied and pasted into WordPress.
#    
#     You are free to redistribute and/or modify wordtex under the
#     terms of the GNU General Public License (GPL), version 3
#     or (at your option) any later version.
#    
#     You should have received a copy of the GNU General Public
#     License along with wordtex.  If you can't find it,
""".format(version = VERSION)
publish.LAST_LINE = '''#     see <http://www.gnu.org/licenses/>'''

publish.CLOUDTB_VERSION_URL = (
        'https://github.com/cloudformdesign/cloudtb/archive/v0.1.1.zip')

if __name__ == '__main__':
    from cloudtb import dbe
    publish.main()