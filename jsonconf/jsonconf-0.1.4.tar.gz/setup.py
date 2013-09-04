#!/usr/bin/python
# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4
# Author: "Chris Ward <cward@redhat.com>

from distutils.core import setup

__version__ = '0.1.4'


with open('readme.rst') as _file:
    readme = _file.read()

github = 'https://github.com/drpoovilleorg/jsonconf'
download_url = '%s/releases/tag/v%s.tar.gz' % (github, __version__)

setup(
    name='jsonconf',
    version=__version__,
    packages=['jsonconf'],
    url='https://github.com/drpoovilleorg/jsonconf',
    license='GPLv3',
    author='Chris Ward',
    author_email='cward@redhat.com',
    download_url=download_url,
    description='Python/JSON Configuration Object',
    long_description=readme,
    data_files=[('jsonconf', ['readme.rst'])],
    classifiers=[
        'Development Status :: 4 - Beta',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Natural Language :: English',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 2 :: Only',
        'Topic :: Utilities',
    ],
    keywords=['json', 'configure', 'config'],
    provides=['jsonconf'],
    requires=[],
    install_requires=[],
    scripts=[]
)
