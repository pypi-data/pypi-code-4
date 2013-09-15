#!/usr/bin/env python
'''
Created on Feb 18, 2013

@author: legion
'''
from setuptools import setup
setup(
	name = "git-repo-hooks",
	version = "1.01.004",
	scripts = ['git-hooks'],

	# Project uses reStructuredText, so ensure that the docutils get
	# installed or upgraded on the target machine
	install_requires = ['kjlib'],

	# metadata for upload to PyPI
    author='K Jonathan',
    author_email='phenixdoc@gmail.com',
    description='A tool to manage project, user, and global Git hooks for multiple git repositories',
    url='https://github.com/legion0/git-repo-hooks',
)

