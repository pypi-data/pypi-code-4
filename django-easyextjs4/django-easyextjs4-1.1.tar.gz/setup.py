#!/usr/bin/env python

from distutils.core import setup

setup(name='django-easyextjs4',
      version='1.1',
      description='Django extension for ExtJS 4 and Sencha Touch',
      author='Christophe Braud',
      author_email='chbperso@gmail.com',
      url='https://github.com/TofPlay/django-easyextjs4',
      download_url='https://github.com/TofPlay/django-easyextjs4/archive/1.1.tar.gz',
      packages=['EasyExtJS4'],
      package_dir={'EasyExtJS4':'EasyExtJS4'},
      package_data={'EasyExtJS4':['LICENCE.txt']},
      classifiers=[
              'Development Status :: 4 - Beta',
              'Environment :: Web Environment',
              'Intended Audience :: Developers',
              'Operating System :: MacOS :: MacOS X',
              'Operating System :: POSIX',
              'Programming Language :: Python',
              ],
)
