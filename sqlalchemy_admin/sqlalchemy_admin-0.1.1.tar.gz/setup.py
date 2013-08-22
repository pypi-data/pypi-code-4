import os

from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))

requires = [
    ]

setup(name='sqlalchemy_admin',
      version='0.1.1',
      description='CRUD admin interface for sqlalchemy',
      author='Stas Kaledin',
      author_email='staskaledin@gmail.com',
      url='',
      packages=["sqlalchemy_admin"],
      install_requires=requires
      )
