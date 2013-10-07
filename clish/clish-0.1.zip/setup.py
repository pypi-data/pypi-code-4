import os
import setuptools


setuptools.setup(
    name = "clish",
    version = "0.1",
    author = "Vitold Sedyshev",
    author_email = "vit1251@gmail.com",
    description = "Command Line Interactive Shell Framework.",
    license = "BSD",
    keywords = "cli command line shell framework readline console",
    url = "https://github.com/vit1251/clish",
    packages = ['clish'],
    package_dir = {'': 'src'},
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Topic :: Utilities",
        "License :: OSI Approved :: BSD License",
    ],
)
