#!/usr/bin/env python

import os

from setuptools import find_packages, setup

setup(
    name='cmsplugin_syntax_highlight',
    version='0.1.0',
    author='Norm Murrin',
    author_email='norman.murrin@gmail.com',
    url='http://github.com/nmurrin',
    license = 'Simplified BSD License',
    description = 'DjangoCMS syntax highlighting plugin allowing '
                  'for easy integration with SyntaxHighlighter.',
    long_description = open(os.path.join(os.path.dirname(__file__), 'README.rst')).read(),
    packages=find_packages(),
    package_data={
        'cmsplugin_syntax_highlight': [
            'static/cmsplugin_syntax_highlight/*',
            'templates/cmsplugin_syntax_highlight/*',
        ]
    },
    classifiers = [
        'Development Status :: 3 - Alpha',
        'Environment :: Plugins',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Framework :: Django',
    ],
    provides=['cmsplugin_syntax_highlight', ],
    include_package_data=True,
    zip_safe = False,
)
