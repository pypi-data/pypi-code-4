#!/usr/bin/env python
from distutils.core import setup

# readme is needed at upload time, not install time:
try:
    with open('readme.rst') as f:
        long_description = f.read().decode('utf8')
except IOError:
    long_description = ''


setup(
    name          = 'ushlex',
    version       = '0.98',
    description   = ('Replacement for shlex (that works with unicode) ' +
                     'for Python 2.X.'),
    author        = 'Eric S. Raymond, Gustavo Niemeyer, Colin Walters',
    author_email  = 'no@reply.com',
    maintainer    = 'Mike Miller',
    maintainer_email = 'no@reply.com',
    url           = 'https://bitbucket.org/mixmastamyk/ushlex',
    download_url  = 'https://bitbucket.org/mixmastamyk/ushlex/get/default.tar.gz',
    py_modules    = ['ushlex'],

    long_description = long_description,
    classifiers     = [
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent ',
        'Programming Language :: Python :: 2',
    ],
)

