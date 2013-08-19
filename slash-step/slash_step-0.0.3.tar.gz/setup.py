from setuptools import setup, find_packages
import functools
import os
import platform

_PYTHON_VERSION = platform.python_version()
_in_same_dir = functools.partial(os.path.join, os.path.dirname(__file__))

with open(_in_same_dir("slash_step", "__version__.py")) as version_file:
    exec(version_file.read())  # pylint: disable=W0122

install_requires = [
    "slash>=0.0.3",
]

setup(name="slash_step",
      classifiers=[
          "Programming Language :: Python :: 2.6",
          "Programming Language :: Python :: 2.7",
          "Programming Language :: Python :: 3.3",
          ],
      description="A more granular sub STEP for slash tests",
      license="BSD",
      author="Omer Gertel",
      author_email="omerg@gmail.com",
      url="https://github.com/omergertel/slash-step",
      version=__version__, # pylint: disable=E0602
      packages=find_packages(exclude=["tests"]),
      install_requires=install_requires,
      )
