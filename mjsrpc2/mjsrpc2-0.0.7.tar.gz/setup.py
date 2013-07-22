import os
from setuptools import setup

def read(fname):
    if os.path.exists(fname):
        return open(os.path.join(os.path.dirname(__file__), fname)).read()


srcdir = os.path.join(os.path.dirname(__file__), 'src')

setup(
    name = "mjsrpc2",
    version = "0.0.7",
    author = "Marian Neagul",
    author_email = "marian@ieat.ro",
    description = "mjsrpc2 is a extension of jsonrpc2 providing introspection and argument type validation",
    license = "APL",
    keywords = "jsonrpc2 rpc",
    url = "http://developers.mosaic-cloud.eu",
    package_dir = {'':srcdir},
    packages = ["mjsrpc2", "mjsrpc2.ui"],
    long_description = read('README.rst'),
    classifiers = [
        "Intended Audience :: Developers",
        "Development Status :: 3 - Alpha",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "License :: OSI Approved :: Apache Software License",
    ],
    entry_points = {
                      'console_scripts': [
                                          'mjsrpc2-cli = mjsrpc2.ui.app:main',
                                          ]
                      },
    setup_requires = ["setuptools_webdav", ],
    install_requires = ['jsonrpc2', "pyyaml>=3.0"]
)
