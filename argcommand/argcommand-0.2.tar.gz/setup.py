from distutils.core import setup
import argcommand

setup(
    name = "argcommand",
    version = argcommand.__version__,
    description = "A Python module that provides simple object-oriented abstraction layer for creating command-line interfaces.",
    author = "Roi Avinoam",
    author_email = "avinoamr@gmail.com",
    url = "https://github.com/avinoamr/argcommand",
    license = "MIT",
    py_modules = [ "argcommand" ]
)