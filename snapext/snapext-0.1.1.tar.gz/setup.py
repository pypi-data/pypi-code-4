import re
from setuptools import setup


version = re.search("__version__ = '([^']+)'",
                    open('snapext/__init__.py').read()).group(1)


setup(name = 'snapext',
      version = version,
      author = 'Tim Radvan',
      author_email = 'blob8108@gmail.com',
      url = 'https://github.com/blob8108/snapext',
      description = 'Server for writing Snap! extensions',
      license = 'MIT',
      packages = ['snapext'],
      classifiers = [
        "Programming Language :: Python",
      ],
)
 
