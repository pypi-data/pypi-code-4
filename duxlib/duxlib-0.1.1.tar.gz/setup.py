from setuptools import setup, find_packages

import duxlib


setup(
    name = 'duxlib',
    version = duxlib.__version__,
    author = 'Daniel Duckworth',
    author_email = 'duckworthd@gmail.com',
    description = "Extensions to Python libraries",
    license = 'BSD',
    keywords = 'libraries extensions',
    url = 'http://github.com/duckworthd/duxlib',
    packages = find_packages(),
    classifiers = [
      'Development Status :: 4 - Beta',
      'License :: OSI Approved :: BSD License',
      'Operating System :: OS Independent',
      'Programming Language :: Python',
    ],

    # since duxlib is more like an amalgamation of minimodules, I'll forgo
    # actually requiring them and instead let the `ImportError`s flow.
    install_requires = [     # dependencies
      # 'bottle>=0.11.6',
      # 'munkres>=1.0.5.4',
      # 'numpy>=1.7.1',
      # 'pandas>=0.12.0',
    ],
)
