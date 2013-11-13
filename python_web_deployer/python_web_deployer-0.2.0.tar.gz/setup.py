import os
from setuptools import setup


# Utility function to read the README file.
# Used for the long_description.  It's nice, because now 1) we have a top level
# README file and 2) it's easier to type in the README file than to put a raw
# string in below ...
def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name = "python_web_deployer",
    version = "0.2.0",
    author = "Kaledin Stas",
    author_email = "staskaledin@gmail.com",
    description = ("Deploy you sites to remote server", ),
    license = "BSD",
    keywords = "web deploy deployment",
    url = "sallyruthstruik.bitbucket.org/python-web-deployer",
    packages=['deploy_class', ],
    scripts = ['deploy',],
    install_requires = [
        'paramiko',
    ], 
    long_description=read('README'),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "License :: OSI Approved :: BSD License",
    ],
)
