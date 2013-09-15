import os

from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))

requires = [
    'pillow'
]

try:
    with open(os.path.join(here, 'README.md')) as f:
        README = f.read()
except:
    README = ''

setup (name = "simplecaptcha",
       version = "0.5",
       description = "A Python framework for CAPTCHA tests",
       maintainer = "Isaac Cook",
       maintainer_email = "isaac@simpload.com",
       author = "Micah Dowty",
       author_email = "micah@navi.cx",
       license = "MIT",
       install_requires=requires,
       packages=['simplecaptcha', 'simplecaptcha.visual'],
       )
