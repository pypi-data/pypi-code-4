
#!/usr/bin/env python
"""tweetup-v1.2 script"""
from setuptools import find_packages, setup

setup(name = 'tweetup-v1.2',
    version = '1.2',
    description = "Tweetup  module.",
    long_description = "A script created to tweet with a media",
    platforms = ["Linux"],
    author="Anurag Kumar",
    author_email="anurag3rdsep@gmail.com",
    url="https://github.com/anurag619/mywork/tree/master/tweet",
    install_requires=["twython", "simplyson", "oauth2", "httlib2"],
    license = "MIT",
    packages=find_packages()
    )
