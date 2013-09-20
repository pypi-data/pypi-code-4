from setuptools import setup

setup(
  name = 'jinjatools',
  version = '0.1a10',
  description = (
    'Various tools for Jinja2,'
    ' including new filters and tests based on moretools,'
    ' a JinjaLoader class for Django,'
    ' and a simple JinjaBuilder class for SCons.'
    ),
  author = 'Stefan Zimmermann',
  author_email = 'zimmermann.code@gmail.com',
  url = 'http://bitbucket.org/userzimmermann/python-jinjatools',

  license = 'LGPLv3',

  install_requires = [
    'moretools >= 0.1a25',
    'Jinja2',
    ],
  packages = [
    'jinjatools',
    'jinjatools.django',
    'jinjatools.scons',
    ],

  classifiers = [
    'Development Status :: 3 - Alpha',
    'Intended Audience :: Developers',
    'License :: OSI Approved ::'
    ' GNU Library or Lesser General Public License (LGPL)',
    'Operating System :: OS Independent',
    'Programming Language :: Python',
    'Programming Language :: Python :: 2',
    'Programming Language :: Python :: 3',
    'Topic :: Software Development',
    'Topic :: Utilities',
    ],
  keywords = [
    'jinja', 'jinja2', 'tools', 'template', 'macro',
    'filter', 'test', 'moretools',
    'scons', 'builder', 'build',
    'django', 'web', 'html',
    ],
  )
