from setuptools import setup, find_packages
import sys, os

version = '0.1'

setup(name='pyramid_auth',
      version=version,
      description="Simple pyramid authentication system",
      long_description=open('README.rst').read(),
      classifiers=[
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Topic :: Internet :: WWW/HTTP',
      ],
      keywords='',
      author='Aur\xc3\xa9lien Matouillot',
      author_email='a.matouillot@gmail.com',
      url='https://github.com/LeResKP/pyramid_auth',
      license='MIT',
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'pyramid',
          'tw2.core',
          'tw2.forms',
          'mako',
          'paste',
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
