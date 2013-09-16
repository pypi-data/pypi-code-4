# coding=utf-8
#
# Copyright (c) 2008-2013 by zenzire - http://www.zenzire.com
# Author Marcin Mierzejewski
#

import os
from setuptools import setup
from setuptools import find_packages

import klisha

setup(
    name='django-klisha',
    version=klisha.__version__,

    description='A standards-compliant and responsive photoblog web application, written in Python and Django',
    long_description=open(os.path.join(os.path.dirname(__file__), 'README.rst')).read(),
    keywords='django, blog, photoblog, weblog, post, news, responsive',

    author=klisha.__author__,
    author_email=klisha.__email__,
    url=klisha.__url__,

    packages=find_packages(exclude=['example']),
    classifiers=[
        'Framework :: Django',
        'Development Status :: 5 - Production/Stable',
        'Environment :: Web Environment',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        'License :: OSI Approved :: BSD License',
        'Topic :: Software Development :: Libraries :: Python Modules'],

    license='BSD',
    platforms=['OS Independent'],
    include_package_data=True,
    zip_safe=False,
    install_requires=[
                      'Django==1.5.2',
                      'PIL==1.1.7',
                      'South==0.7.6',
                      'django-compressor==1.3',
                      'django-pure-pagination==0.2.1',
                      'sorl-thumbnail==11.12',
                      'django-admin-bootstrapped==0.4.1']
)
