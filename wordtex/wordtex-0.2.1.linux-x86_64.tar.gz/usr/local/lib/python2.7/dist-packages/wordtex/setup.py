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
#!/usr/bin/env python

from distutils.core import setup
import publish
setup(name='wordtex',
      version=publish.VERSION,
      description='Latex to Word Press HTML converter',
      author='Garrett Berg',
      author_email='garrett@cloudformdesign.com',
      url='https://github.com/cloudformdesign/wordtex',
#          modules = ['wordtex', 'wp_formatting', 'texlib'],
      packages = ['wordtex', 'wordtex.cloudtb',],
      package_dir = {'wordtex': '_publish'}
#      packages=['wordtex', 'wordtex.cloudtb'],
     )
    