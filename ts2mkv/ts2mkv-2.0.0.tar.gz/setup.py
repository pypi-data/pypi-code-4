#!/usr/bin/python
import sys

name = 'ts2mkv'
version = '2.0.0'
author = 'Jaakko Vuori'
author_email = "jaakko.vuori@gmail.com"
scripts = ['bin/ts2mkv', 'bin/mkvenc']
if sys.platform == 'win32':
    scripts.extend(['bin/ts2mkv.cmd', 'bin/mkvenc.cmd'])
url = 'https://bitbucket.org/ts2mkv/ts2mkv'
license = 'LICENSE.txt'
classifiers = [
        "Programming Language :: Python",
        "Programming Language :: Python :: 2.7",
        "Environment :: Console",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: MIT License",
        "Operating System :: POSIX :: Linux",
        "Operating System :: Microsoft :: Windows",
        "Topic :: Multimedia :: Sound/Audio :: Conversion",
        ]
description = 'Converts DVB Transport Stream (.ts) files into Matroska (.mkv)'
long_description = open('README.rst').read()

def setup_py2exe():
    from distutils.core import setup
    import py2exe
    from glob import glob
    data_files = [('.', glob('ts2mkv/*.ini')),
        ('.', ['ts2mkv/ProjectX.jar', 'ts2mkv/colours.tbl']),
        ('lib', glob('ts2mkv/lib/*.*')),
        ('dll', glob('ts2mkv/dll/*.*')),]
    py2exe_options = dict(
        ascii=True,
        excludes=['_ssl', '_hashlib', 'pyreadline', 'difflib', 'doctest', 'optparse', 'calendar', 'socket', 'urllib', 'tarfile', 'xmlrpclib', 'zipfile'],
    )
    setup(
        name=name,
        version=version,
        author=author,
        scripts=scripts,
        url=url,
        license=license,
        description=description,
        long_description=long_description,
        console=['bin/ts2mkv', 'bin/mkvenc'],
        data_files=data_files,
        options={'py2exe': py2exe_options},
    )

def setup_setuptools():
    from setuptools import setup, find_packages
    setup(
        name=name,
        version=version,
        author=author,
        author_email=author_email,
        packages=find_packages(),
        scripts=scripts,
        include_package_data=True,
        url=url,
        license=license,
        description=description,
        long_description=long_description,
        zip_safe=False,
        classifiers=classifiers,
    )

if __name__ == '__main__':
    if sys.argv[1] == 'py2exe':
        setup_py2exe()
        from distutils.archive_util import make_archive
        import platform
        make_archive('ts2mkv-%s-win-%s' % (version, platform.machine().lower()), 'zip', 'dist')
    else:
        setup_setuptools()
