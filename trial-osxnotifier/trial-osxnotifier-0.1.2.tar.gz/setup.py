import os

from setuptools import setup

from trialosxnotifier import __version__


def refresh_plugin_cache():
    from twisted.plugin import IPlugin, getPlugins
    list(getPlugins(IPlugin))


with open(os.path.join(os.path.dirname(__file__), "README.rst")) as readme:
    long_description = readme.read()

classifiers = [
    "Development Status :: 3 - Alpha",
    "License :: OSI Approved :: MIT License",
    "Operating System :: OS Independent",
    "Programming Language :: Python",
    "Programming Language :: Python :: 2.6",
    "Programming Language :: Python :: 2.7",
    "Programming Language :: Python :: 3.2",
    "Programming Language :: Python :: 3.3",
    "Programming Language :: Python :: 2",
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: Implementation :: CPython",
    "Programming Language :: Python :: Implementation :: PyPy"
]

setup(
    name="trial-osxnotifier",
    version=__version__,
    py_modules=["trialosxnotifier"],
    packages=["twisted.plugins"],
    package_data={"twisted" : ["plugins/trial_osxnotify.py"]},
    author="Julian Berman",
    author_email="Julian@GrayVines.com",
    classifiers=classifiers,
    description="A Trial reporter that reports with OS X notifications",
    license="MIT",
    long_description=long_description,
    url="https://github.com/Julian/trial-osxnotifier",
)

refresh_plugin_cache()
