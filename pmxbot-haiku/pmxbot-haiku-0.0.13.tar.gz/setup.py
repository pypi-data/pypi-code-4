import re


module_file = open("pmxbot_haiku/__init__.py").read()
metadata = dict(re.findall("__([a-z]+)__\s*=\s*'([^']+)'", module_file))
long_description = open('README.rst').read()

from setuptools import setup, find_packages

setup(
    name         = 'pmxbot-haiku',
    description  = 'Enable haikus on pmxbot',
    packages     = find_packages(),
    author       = 'Alfredo Deza',
    author_email = 'contact [at] deza.pe',
    version      = metadata['version'],
    url          = 'http://github.com/alfredodeza/pmxbot-haiku',
    license      = "MIT",
    zip_safe     = False,
    keywords     = "haiku, irc, bot",
    entry_points = {
        'pmxbot_handlers': [
            'haiku = pmxbot_haiku.haiku:init_models',
        ],
    },
    # XXX
    #long_description = long_description,
    classifiers      = [
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Topic :: Software Development :: Libraries',
        'Topic :: Utilities',
        'Operating System :: MacOS :: MacOS X',
        'Operating System :: Microsoft :: Windows',
        'Operating System :: POSIX',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.0',
        'Programming Language :: Python :: 3.1',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: Implementation :: PyPy'
    ]
)
