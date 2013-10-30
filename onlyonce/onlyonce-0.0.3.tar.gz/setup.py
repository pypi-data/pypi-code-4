from distutils.core import setup
from onlyonce import __version__

setup(
    name = 'onlyonce',
    py_modules = ['onlyonce'],
    scripts = ['onlyonce.py'],
    version = __version__,
    description = 'Small Python lib for running scripts once and once only (with file locks, etc)',
    long_description=open('README.rst','r').read(),
    author = 'Daniel Fairhead',
    author_email = 'danthedeckie@gmail.com',
    url = 'https://github.com/danthedeckie/onlyonce',
    download_url = 'https://github.com/danthedeckie/onlyonce/tarball/' + __version__,
    keywords = ['Files', 'Process Locking', 'Scripting'],
    classifiers = ['Development Status :: 4 - Beta',
                   'License :: OSI Approved :: MIT License',
                   'Intended Audience :: Developers',
                   'Programming Language :: Python :: 2.7',
                   'Environment :: Console',
                   'Intended Audience :: System Administrators',
                   'Topic :: Software Development :: Libraries',
                   'Topic :: System :: Systems Administration',
                  ],
    )
