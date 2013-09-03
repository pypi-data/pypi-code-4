# coding: utf-8
from setuptools import setup
import pulpitum

setup(name='pulpitum',
      version=pulpitum.__version__,
      author="Sofia Velmer",
      author_email="me@require.pm",
      description='PyPI client for Humans™',
      license="GNU GPLv3",
      keywords="pypi packages",
      url="https://github.com/requirements/pulpitum",
      packages=['pulpitum'],
      package_dir={'pulpitum': 'pulpitum'},
      provides=['pulpitum'],
      classifiers=[
          'Intended Audience :: Developers',
          'Development Status :: 3 - Alpha',
          'Operating System :: OS Independent',
          'Programming Language :: Python',
          'Programming Language :: Python :: 2.7',
          'Programming Language :: Python :: 3.3',
          'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
      ],
      platforms=['All'],
      install_requires=[
          'pkgtools',
      ],
      )
