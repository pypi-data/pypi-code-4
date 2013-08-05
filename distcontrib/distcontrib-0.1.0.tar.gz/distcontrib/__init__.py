#!/usr/bin/env python

pkg_name         = __name__ if __package__ is None else __package__
pkg_description  = 'Contributions to Distutils'
pkg_version      = '0.1.0'
pkg_license      = 'OSI Approved :: BSD License'
pkg_url          = 'http://' + pkg_name + '.readthedocs.org/'
pkg_author       = 'Richard Gomes http://rgomes-info.blogspot.com'
pkg_email        = 'rgomes.info@gmail.com'
pkg_keywords     = [ 'distribute','setuptools','pip','cython' ]
pkg_requirements = []

import tools
from command.doctest import doctest as doctest
from command.zap     import zap
