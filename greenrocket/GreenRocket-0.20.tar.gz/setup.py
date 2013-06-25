from distribute_setup import use_setuptools

use_setuptools()

import os
import sys
from setuptools import setup

version = '0.20'
here = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(here, 'README.rst')).read()
CHANGES = open(os.path.join(here, 'CHANGES.rst')).read()

requires = []
if sys.version_info[0] == 2 and sys.version_info[1] == 6:
    requires.append('weakrefset')

setup(
    name='GreenRocket',
    version=version,
    description='A simple and compact implementation '
                'of Observer design pattern',
    long_description=README + '\n\n' + CHANGES,
    classifiers=[
        'License :: OSI Approved :: BSD License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: Implementation :: PyPy',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Intended Audience :: Developers',
    ],
    keywords='',
    author='Dmitry Vakhrushev',
    author_email='self@kr41.net',
    url='https://bitbucket.org/kr41/greenrocket',
    download_url='https://bitbucket.org/kr41/greenrocket/downloads',
    license='BSD',
    py_modules=['greenrocket'],
    install_requires=requires,
    zip_safe=True,
)
