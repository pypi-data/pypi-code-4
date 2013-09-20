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

long_description = read('README.md')

setup(name="iampq",
      packages=find_packages(),
      version=find_version('iampq', '__version__.py'),
      description="A non-blocking thin pika wrapper that adapts logic of kombu.",
      long_description = long_description,
      classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Topic :: Software Development :: Build Tools',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.1',
        'Programming Language :: Python :: 3.2',
      ],
      keywords='amqp rabbitmq pika tornado',
      author='Rustem Kamun',
      author_email='r.kamun@gmail.com',
      url='https://bitbucket.org/Rustem/iampq',
      license='MIT',
      install_requires=['tornado>=3.0', 'pika>=0.9'],
      zip_safe=False,
      )
