"""metadata_utils installation script.
"""
import os

from setuptools import setup
from setuptools import find_packages

here = os.path.abspath(os.path.dirname(__file__))
README = ''
try: 
    README = open(os.path.join(here, "README.md")).read()
    README = README.split("\n\n", 1)[0] + "\n"
except:
    pass

requires = []

setup(name="metadata_utils",
      description="Lightweight Metadata Support",
      version="0.0.1",
      url="https://github.com/jvanasco/metadata_utils",
      author="Jonathan Vanasco",
      author_email="jonathan@findmeon.com",
      long_description=README,
      zip_safe=False,
      keywords="web",
      test_suite="tests",
      packages=find_packages(),
      include_package_data=True,
      classifiers=[
        "Intended Audience :: Developers",
        "Programming Language :: Python",
        "License :: OSI Approved :: MIT License",
        ],
      license="MIT",
      )

