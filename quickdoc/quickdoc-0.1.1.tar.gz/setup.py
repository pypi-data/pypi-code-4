
from setuptools import setup

setup(
    name="quickdoc",
    version="0.1.1",
    description="TBD",
    author="Alexander Boyd",
    author_email="alex@opengroove.org",
    py_modules=["quickdoc_generator"],
    install_requires=["fileutils", "singledispatch"],
    entry_points = {
        "console_scripts": [
            "quickdoc = quickdoc_generator:main"
        ]
    }
)
