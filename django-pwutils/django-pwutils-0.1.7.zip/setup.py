# -*- coding: utf-8 -
#
# This file is part of django-pwutils released under the MIT license. 
# See the LICENSE for more information.

import os
from setuptools import setup, find_packages

tests_require = [
    'django-webtest>=1.5.7,<2.0',
    'webtest>=2.0.6,<3.0',

    'coverage==3.5.3',
    'django-coverage',

    'django-whatever',

    #tests jenkins
    'django-jenkins>=0.12.1',
    'pyflakes',
    'pylint',
    'pep8>1.2',
]

setup(
    name='django-pwutils',
    version=__import__('pwutils').VERSION,
    description='Django specific utils and helpers',
    long_description=file(
        os.path.join(
            os.path.dirname(__file__),
            'README.md'
        )
    ).read(),
    author='Suvit Org',
    author_email='mail@suvit.ru',
    license='MIT',
    url='http://bitbucket.org/suvitorg/django-pwutils',
    zip_safe=False,
    packages=find_packages(exclude=['docs', 'examples', 'tests']),
    #install_requires='#django<1.4',
    extras_require = {
        'celery': ["django-celery>=2.3.3"],
        'storages': ['pytils'],
        'thumbs': ["Pillow<2.0",
                   "sorl-thumbnail"],
        'sphinxsearch': ['elementflow',
                         'django-sphinx'],
        'tests': tests_require,
        'admintools': ['django-admin-tools>=0.5.1',
                       'FeedParser'],
        'devel': ['django-debug-toolbar',
                 ],
    },
    tests_require=tests_require,
    include_package_data=True,
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Framework :: Django',
        'License :: OSI Approved :: MIT License',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Environment :: Web Environment',
        'Topic :: Software Development',
    ]

)
