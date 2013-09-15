import os

from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))

try:
    with open(os.path.join(here, 'README.rst')) as f:
        README = f.read()
except:
    README = ''

setup (name = "pysistor",
       version = "0.1",
       description = "A Python framework for CAPTCHA tests",
       author="Isaac Cook",
       author_email="isaac@simpload.com",
       license = "MIT",
       test_suite="yota.tests",
       install_requires=[],
       package_dir={'': "src"}
       )
