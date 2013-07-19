#!/usr/bin/env python

#
# Copyright 2009, Michael R <none@example.com>
# All rights reserved. Distributed under the terms of the MIT License.
#

from setuptools import setup

install_requires = ['Trac>=0.12.2']


# ........................................................................... #
def main():
    setup(
        version='0.2.1',
        description='Provides support for sub ticket types in the Trac interface.',
        name='trac-subtickettypes',
        author='Michael R',
        author_email='',
        package_data={'subtickettypes': ['htdocs/*.js']},
        license='BSD',
        install_requires=install_requires,
        packages=['subtickettypes'],
        url='https://github.com/goodwillcoding/trac-subtickettypes',
        keywords='trac plugin ticket types subtickettypes',
        classifiers=[
            'Framework :: Trac',
            'Environment :: Web Environment',
            'Framework :: Trac',
            'License :: OSI Approved :: BSD License',
            'Natural Language :: English',
            'Operating System :: OS Independent',
            'Programming Language :: Python',
        ],
        entry_points={
            'trac.plugins': [
                'subtickettypes.web_ui=subtickettypes.web_ui',
            ]
        }
    )


# =========================================================================== #
if __name__ == "__main__":
    main()
