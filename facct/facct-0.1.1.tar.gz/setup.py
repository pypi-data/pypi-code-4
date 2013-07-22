#!/usr/bin/env python
#-*- coding: utf-8 -*-
import setuptools
import re
import facct as package

setuptools.setup(
    name                 = package.__name__,
    version              = package.__version__,
    description          = package.__doc__.partition('\n\n')[0],
    long_description     = package.__doc__.partition('\n\n')[2],
    author               = package.__author__,
    author_email         = package.__author_email__,
    license              = package.__license__,
    url                  = package.__url__,
    classifiers          = re.findall(r'\S[^\n]*', package.__classifiers__),
    packages             = setuptools.find_packages(),
    include_package_data = True,
    zip_safe             = True,
)
