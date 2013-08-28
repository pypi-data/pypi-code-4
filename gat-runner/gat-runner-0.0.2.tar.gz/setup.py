#from distutils.core import setup
from setuptools import setup, find_packages

VERSION = "0.0.2"
PROJECT_NAME = 'gat-runner'

tests_require = [
]

install_requires = [
  'six==1.3.0',
  'simplejson==3.1.3',
  'gat-games==0.0.2',
]

setup(name='%s' % PROJECT_NAME,
      url='https://github.com/gatournament/%s' % PROJECT_NAME,
      author="gatournament",
      author_email='info@gatournament.com',
      keywords='gat game algorithms tournament',
      description='GAT Runner',
      license='MIT',
      classifiers=[
          'Operating System :: OS Independent',
          'Topic :: Software Development'
      ],

      version='%s' % VERSION,
      install_requires=install_requires,
      tests_require=tests_require,
      # test_suite='runtests.runtests',
      # extras_require={'test': tests_require},

      packages=find_packages(),
)
