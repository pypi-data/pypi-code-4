#from distutils.core import setup
from setuptools import setup, find_packages

VERSION = '0.0.3'
PROJECT_NAME = 'gat-python'

tests_require = [
    'nose',
    'coverage',
]

install_requires = [
    'six==1.3.0',
    'simplejson==3.1.3',
]

setup(name='%s' % PROJECT_NAME,
      url='https://github.com/gatournament/%s' % PROJECT_NAME,
      author="gatournament",
      author_email='contact@gatournament.com',
      keywords='',
      description='',
      license='MIT',
      classifiers=[
          'Operating System :: OS Independent',
          'Topic :: Software Development'
      ],

      version='%s' % VERSION,
      install_requires=install_requires,
      tests_require=tests_require,

      packages=find_packages(),
)

