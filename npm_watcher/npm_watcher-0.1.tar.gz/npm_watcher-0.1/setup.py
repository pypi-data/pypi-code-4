#!/usr/local/bin/python

from distutils.core import setup

setup(name='npm_watcher',
      version='0.1',
      author='Kevin Smithson',
      author_email='ksmithson@sazze.com',
      description='NPM Install File Watcher',
      scripts = [
        'scripts/npm_watcher'
    ], requires=['watchdog']
)