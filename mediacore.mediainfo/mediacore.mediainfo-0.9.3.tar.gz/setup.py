from setuptools import setup, find_packages
import os

version = '0.9.3'

long_description = (
    open('README.txt').read()
    )

setup(name='mediacore.mediainfo',
      version=version,
      description="Mediacore.mediainfo provides info about media file as JSON",
      long_description=long_description,
      # Get more strings from
      # http://pypi.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Programming Language :: Python",
        ],
      keywords='Mediacore ',
      author='RedTurtle',
      author_email='sviluppoplone@redturtle.it',
      url='',
      license='gpl',
      packages=find_packages('src'),
      package_dir = {'': 'src'},
      namespace_packages=['mediacore'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'Mediacore',
          # -*- Extra requirements: -*-
      ],
      entry_points = {
          'mediacore.plugin': [
              'mediainfo = mediacore.mediainfo.media_metadata',
          ],
        }
      )
