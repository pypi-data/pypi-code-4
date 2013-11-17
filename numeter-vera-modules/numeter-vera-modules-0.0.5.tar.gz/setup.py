#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# $Id: setup.py,v 0.2.3.4 2013-11-15 09:56:56 Seraf Exp $
#
# Copyright (C) 2013  Julien Syx (Seraf) <julien@syx.fr>
#
#The MIT License (MIT)
#
#Permission is hereby granted, free of charge, to any person obtaining a copy of
#this software and associated documentation files (the "Software"), to deal in
#the Software without restriction, including without limitation the rights to
#use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of
#the Software, and to permit persons to whom the Software is furnished to do so,
#subject to the following conditions:
#
#The above copyright notice and this permission notice shall be included in all
#copies or substantial portions of the Software.
#
#THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS
#FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR
#COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER
#IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN
#CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
from distutils.core import setup


if __name__ == '__main__':

    setup(name='numeter-vera-modules',
          version='0.0.5',
          description='Numeter Vera Poller modules',
          long_description="""A Vera module for Numeter poller.""",
          author='Julien Syx',
          author_email='julien@syx.fr',
          maintainer='Julien Syx',
          maintainer_email='julien@syx.fr',
          keywords=['numeter','graphing','poller','vera','homeautomation'],
          url='https://github.com/Seraf/numeter-vera-modules',
          license='MIT',
          packages = [''],
          package_data={'': ['veraModule.py']},
          classifiers=[
              'Development Status :: 4 - Beta',
              'Environment :: Console',
              'Intended Audience :: End Users/Desktop',
              'Intended Audience :: System Administrators',
	      'License :: OSI Approved :: MIT License',
              'Operating System :: POSIX',
              'Programming Language :: Python',
              'Topic :: System :: Monitoring'
          ],
         )
