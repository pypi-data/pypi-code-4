# This should be only one line. If it must be multi-line, indent the second
# line onwards to keep the PKG-INFO file format intact.
"""Disable SSL verification of setuptools for buildout
"""

from setuptools import setup, find_packages
import glob
import os.path


def project_path(*names):
    return os.path.join(os.path.dirname(__file__), *names)


setup(
    name='buildout.disablessl',
    version='1.0',

    install_requires=[
        'setuptools',
    ],

    entry_points={
        'zc.buildout.extension': [
            'default = buildout.disablessl:extension',
        ],
    },

    author='Wolfgang Schnerring <ws@gocept.com>',
    author_email='ws@gocept.com',
    license='ZPL 2.1',
    url='https://bitbucket.org/gocept/buildout.disablessl/',

    keywords='',
    description=__doc__.strip(),
    long_description='\n\n'.join(open(project_path(name)).read() for name in (
        'README.txt',
        'HACKING.txt',
        'CHANGES.txt',
    )),

    namespace_packages=['buildout'],
    packages=find_packages('src'),
    package_dir={'': 'src'},
    include_package_data=True,
    data_files=[('', glob.glob(project_path('*.txt')))],
    zip_safe=False,
)
