#from distutils.core import setup
from setuptools import setup

import pygencad

setup(name='pygencad',
      version=pygencad.__version__,
      author='Ed Blake',
      author_email='kitsu.eb@gmail.com',
      url='https://bitbucket.org/kitsu/pygencad',
      description='Generate command scripts for several CAD applications.',
      long_description=pygencad.__doc__,
      license="Modified BSD",
      packages=['pygencad'],
      package_data={'pygencad': ['SVGPan.js']},
      data_files=[('', ['README.rst', 'LICENSE.txt'])],
      zip_safe = False,
      keywords=['CAD', 'Automation', 'AutoCAD', 'MicroStation'],
      classifiers=[
          'Development Status :: 3 - Alpha',
          'Environment :: Console',
          'Intended Audience :: Developers',
          'License :: OSI Approved :: BSD License',
          'Operating System :: OS Independent',
          'Programming Language :: Python',
          'Programming Language :: Python :: 2.7',
          'Topic :: Scientific/Engineering :: Visualization',
          'Topic :: Software Development :: Libraries :: Python Modules',
          'Topic :: Utilities',
      ],
)
