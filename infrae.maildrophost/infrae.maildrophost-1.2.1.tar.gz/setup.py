# -*- coding: utf-8 -*-
# Copyright (c) 2007-2009 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id: setup.py 33526 2009-02-13 11:11:59Z sylvain $

from setuptools import setup, find_packages

name = "infrae.maildrophost"
setup(name = name,
      version = "1.2.1",
      author = "Sylvain Viollon",
      author_email = "info@infrae.com",
      description = "Recipe to install and setup maildrophost server",
      long_description = open('README.txt').read() + \
          open('docs/HISTORY.txt').read(),
      license = "ZPL 2.1",
      keywords = "maildrophost buildout",
      classifiers = ["Framework :: Buildout",
                     ],
      url = 'http://www.python.org/pypi/' + name,
      packages = find_packages(),
      namespace_packages = ['infrae'],
      install_requires = [
        'zc.buildout',
        'zc.recipe.egg',
        'setuptools'],
      entry_points = {
        'zc.buildout':
            ['default = %s:Recipe' % name]},
    )
