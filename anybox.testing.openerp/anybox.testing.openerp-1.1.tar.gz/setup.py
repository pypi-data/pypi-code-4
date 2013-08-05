import os
import sys
from setuptools import setup, find_packages

version = '1.1'

if sys.version_info < (2, 6):
    sys.stderr.write("This package requires Python 2.6 or newer. "
                     "Yours is " + sys.version + os.linesep)
    sys.exit(1)

requires = ['setuptools',
            ]

setup(
    name="anybox.testing.openerp",
    version=version,
    author="Anybox",
    author_email="contact@anybox.fr",
    description="Useful testing base classes and tools for OpenERP",
    license="AGPL v3+",
    long_description='\n'.join((
        open('README.rst').read(),
        open('CHANGES.rst').read())),
    url="https://bitbucket.org/anybox/anybox.testing.openerp",
    packages=find_packages(),
    zip_safe=False,
    include_package_data=True,
    install_requires=requires,
    tests_require=requires,
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    entry_points={},
)
