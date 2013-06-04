# Copyright (c) 2012 gocept gmbh & co. kg
# See also LICENSE.txt

"""A paste.script template following gocept Python package conventions.
"""

from setuptools import setup, find_packages
import glob
import os.path


def project_path(*names):
    return os.path.join(os.path.dirname(__file__), *names)


setup(
    name='gocept.package',
    version='1.1',

    install_requires=[
        'PasteScript',
        'distribute',
        'pkginfo>=0.9',
        ],

    extras_require={
        'doc': [
            'Sphinx>=1.0',
            ],
        'test': [
            'gocept.testing',
            'unittest2',
            ],
        },

    entry_points={
        'console_scripts': [
            'doc=gocept.package.doc:main',
            ],
        'paste.paster_create_template': [
            'gocept-package = gocept.package.skeleton:Skeleton'
            ],
        },

    author=('Thomas Lotze <tl at gocept dot com> and '
            'Wolfgang Schnerring <ws at gocept dot com>'),
    author_email='mail@gocept.com',
    license='ZPL 2.1',
    url='https://bitbucket.org/gocept/gocept.package/',

    keywords='paste.script paster create template python package sphinx theme',
    classifiers="""\
Environment :: Plugins
Framework :: Paste
Intended Audience :: Developers
License :: OSI Approved :: Zope Public License
Programming Language :: Python
Programming Language :: Python :: 2
Programming Language :: Python :: 2.6
Programming Language :: Python :: 2.7
Programming Language :: Python :: 2 :: Only
"""[:-1].split('\n'),
    description=__doc__.strip(),
    long_description='\n\n'.join(open(project_path(name)).read() for name in (
            'README.txt',
            'HACKING.txt',
            'CHANGES.txt',
            )),

    namespace_packages=['gocept'],
    packages=find_packages('src'),
    package_dir={'': 'src'},
    include_package_data=True,
    data_files=[('', glob.glob(project_path('*.txt')))],
    zip_safe=False,
    )
