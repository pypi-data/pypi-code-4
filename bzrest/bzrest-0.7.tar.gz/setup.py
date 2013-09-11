from setuptools import setup

from bzrest import __version__

setup(
    name="bzrest",
    version=__version__,
    description="A client for Bugzilla's native REST API.",
    author="Ben Hearsum",
    packages=["bzrest"],
    zip_safe=False,
    install_requires=[
        "requests>=1.2.3",
    ],
)
