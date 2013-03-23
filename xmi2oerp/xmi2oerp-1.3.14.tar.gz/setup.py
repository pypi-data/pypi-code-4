#!/usr/bin/env python
##############################################################################
#
#    XMI2OERP, XMI convesort to OpenERP module
#    Copyright (C) 2012 Coop Trab Moldeo Interactive, Grupo AdHoc S.A.
#    (<http://www.moldeointeractive.com.ar>; <www.grupoadhoc.com.ar>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from setuptools import setup

setup(name='xmi2oerp',
      version='1.3.14',
      author='Cristian S. Rocha',
      author_email='cristian.rocha@moldeointeractive.com.ar',
      maintainer='Cristian S. Rocha',
      maintainer_email='cristian.rocha@moldeo.coop',
      url='http://www.moldeointeractive.com.ar/',
      description='XMI Conversor to OpenERP modules.',
      long_description="""
      With this command you can create OpenERP modules from a UML description in XMI file or UML file generated by ArgoUML.
      """,
      classifiers=[
          'Development Status :: 5 - Production/Stable',
          'Environment :: Console',
          'Intended Audience :: Developers',
          'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
          'Natural Language :: English',
          'Operating System :: Unix',
          'Programming Language :: Python :: 2.6',
          'Topic :: Software Development :: Build Tools',
      ],
      scripts=['xmi2oerp/scripts/xmi2oerp'],
      packages=['xmi2oerp'],
      test_suite='xmi2oerp.test',
      install_requires=['Genshi','sqlalchemy'],
      package_data={'xmi2oerp': [
          'data/OpenObjectStadardElements.xmi',
          'data/template/README',
          'data/template/*.*',
          'data/template/view/*',
          'data/template/workflow/*',
          'data/template/data/*',
          'data/template/security/*',
          'data/template/report/*',
          'data/template/wizard/*',
          'data/licenses/*',
      ]},
      dependency_links=[],
   )

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
