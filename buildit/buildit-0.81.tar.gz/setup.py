#!/usr/bin/env python
import sys
from distutils.core import setup, Command

class PyTest(Command):
    user_options = []
    def initialize_options(self):
        pass
    def finalize_options(self):
        pass
    def run(self):
        from subprocess import call
        errno = call([sys.executable, 'buildit/test/runtests.py'])
        raise SystemExit(errno)

# grab metadata
version = '1.00'
with open('buildit/__init__.py') as f:
    for line in f:
        if line.lstrip().startswith('__version__'):
            try:
                version = line.split("'")[1]
            except IndexError:
                pass
            break

# readme is needed at upload time, not install time
try:
    with open('readme.rst') as f:                  # no unicode for older vers.
        long_description = f.read().decode('utf8') #.encode('ascii', 'replace')
except IOError:
    long_description = ''

# do we need modules installed?
requires = []
if sys.version < '3.0':
    requires.append('ushlex')
if sys.version < '2.7':
    requires.append('ordereddict')


setup(
    name          = 'buildit',
    version       = version,
    description   = 'A simple build tool for small projects.',
    author        = 'Mike Miller',
    author_email  = 'mixmastamyk@bitbucket.org',
    url           = 'https://bitbucket.org/mixmastamyk/buildit',
    download_url  = 'https://bitbucket.org/mixmastamyk/buildit/get/default.tar.gz',
    license       = 'GPLv3+',
    scripts       = ['buildit/bld'],
    packages      = ['buildit', 'buildit.test'],
    requires      = requires,
    install_requires = requires,
    cmdclass      = {'test': PyTest},

    long_description = long_description,
    classifiers     = [
        'Development Status :: 3 - Alpha',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: ' +
        'GNU General Public License v3 or later (GPLv3+)',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.6',
        'Topic :: Software Development :: Build Tools',
    ],
)
