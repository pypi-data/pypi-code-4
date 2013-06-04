from distutils.core import setup

setup(
  name             = 'Fangorn',
  version          = '0.2.1',
  author           = 'saaj',
  author_email     = 'mail@saaj.me',
  packages         = ['fangorn', 'fangorn.compat', 'fangorn.test'],
  package_data     = {'fangorn.test' : ['fixture/*']},
  url              = 'http://code.google.com/p/fangorn-py/',
  license          = 'LGPL',
  description      = 'Nested Sets SQL Tree for Python',
  long_description = open('README.txt').read(),
  platforms        = ['Any'],
  classifiers      = [
    'Topic :: Database',
    'Programming Language :: Python :: 2.7',
    'Intended Audience :: Developers'
  ]
)