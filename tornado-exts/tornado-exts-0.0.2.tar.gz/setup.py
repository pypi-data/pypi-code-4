import codecs
import os
import re
from setuptools import setup, find_packages


def read(*parts):
    return codecs.open(os.path.join(os.path.abspath(os.path.dirname(__file__)), *parts), 'r').read()


def find_version(*file_paths):
    version_file = read(*file_paths)
    version_match = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]",
                              version_file, re.M)
    if version_match:
        return version_match.group(1)
    raise RuntimeError("Unable to find version string.")

long_description = read('README')

setup(name="tornado-exts",
      version=find_version('tornado_extensions', '__init__.py'),
      description="A python module that contain common definitions for Django and Tornado game project",
      long_description=long_description,
      classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Topic :: Software Development :: Build Tools',
        'Programming Language :: Python :: 2.7',
      ],
      keywords='django tornado common',
      author='Rustem Kamun, German Ilyin, Cool Max',
      author_email='r.kamun@gmail.com',
      url='https://bitbucket.org/Rustem/iogame-tor-exts',
      license='MIT',
      packages=find_packages(),
      zip_safe=False,

      )
