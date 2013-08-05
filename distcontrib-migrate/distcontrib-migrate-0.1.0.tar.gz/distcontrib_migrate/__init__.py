#!/usr/bin/env python

pkg_name         = 'distcontrib-migrate' #-- __name__ if __package__ is None else __package__
pkg_description  = 'Contributions to Distutils'
pkg_version      = '0.1.0'
pkg_license      = 'OSI Approved :: BSD License'
pkg_url          = 'http://' + pkg_name + '.readthedocs.org/'
pkg_author       = 'Richard Gomes http://rgomes-info.blogspot.com'
pkg_email        = 'rgomes.info@gmail.com'
pkg_keywords     = [ 'distribute', 'setuptools', 'pip', 'sqlalchemy', 'migrate']
pkg_requirements = [ ]


from dsn              import dsn
from command.migrate  import migrate
from command.psql     import psql
