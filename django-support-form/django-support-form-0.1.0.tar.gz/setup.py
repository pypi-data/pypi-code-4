import sys
from setuptools import setup, find_packages

kwargs = {
    # Packages
    'packages': find_packages(exclude=['tests', '*.tests', '*.tests.*', 'tests.*']),
    'include_package_data': True,

    # Dependencies
    'install_requires': [
        'django>=1.4,<1.6',
    ],

    'test_suite': 'test_suite',

    # Metadata
    'name': 'django-support-form',
    'version': __import__('supportform').get_version(),
    'author': 'Byron Ruth',
    'author_email': 'b@devel.io',
    'description': 'Simple support/contact form for your Django app',
    'license': 'BSD',
    'keywords': 'support contact form',
    'url': 'https://github.com/cbmi/django-support-form/',
    'classifiers': [
        'Development Status :: 5 - Production/Stable',
        'License :: OSI Approved :: BSD License',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Framework :: Django',
        'Topic :: Internet :: WWW/HTTP',
        'Intended Audience :: Developers',
    ],
}

setup(**kwargs)
