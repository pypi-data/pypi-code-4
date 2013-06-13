import os
from distutils.core import setup


def package_full(package):
    packages = []
    for path, dirs, files in os.walk(package):
        for file in files:
            if file != '__init__.py':
                continue
            packages.append('.'.join(name for name in path.split(os.path.sep)
                                     if name))
    return packages

setup(name='pretzel',
      version='1.0.2',
      author='Pavel Aslanov',
      description='Pretzel asynchronous python framework',
      long_description=open('README.rst').read(),
      url='https://github.com/aslpavel/pretzel',
      packages=package_full('pretzel'))
