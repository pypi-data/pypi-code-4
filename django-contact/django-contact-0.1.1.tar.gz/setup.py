#!/usr/bin/env python

try:
    from setuptools import setup

except ImportError:
    from ez_setup import use_setuptools
    use_setuptools()

    from setuptools import setup

import os

parent_directory = os.path.abspath(os.path.dirname(__file__))

meta_files = {
    'README.md': None,
    'CLASSIFIERS.txt': None,
}

for filename in meta_files:
    try:
        current_file = open(os.path.join(parent_directory, filename))
        meta_files[filename] = current_file.read()
        current_file.close()
    except IOError:
        raise IOError('{0} not found.'.format(filename))

classifiers = meta_files['CLASSIFIERS.txt'].split('\n')
classifiers.remove('')

setup(name='django-contact',
      description='System for working with contacts/identities in django.',
      long_description=meta_files['README.md'],

      version='0.1.1',
      classifiers=classifiers,

      author='Brandon R. Stoner',
      author_email='monokrome@limpidtech.com',
      url='http://github.com/LimpidTech/django-contact',

      packages=['contact'],
      keywords='web django menu navigation',

      zip_safe=False,

      install_requires=[
          'django-model-utils >= 1.4.0, < 2.0',
      ])
