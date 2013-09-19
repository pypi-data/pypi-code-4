import os
import re
from setuptools import setup, find_packages

VERSIONFILE = "flea/__init__.py"


def get_version():
    with open(VERSIONFILE, 'rb') as f:
        return re.search("^__version__\s*=\s*['\"]([^'\"]*)['\"]",
                           f.read().decode('UTF-8'), re.M).group(1)


def read(*path):
    """
    Return content from ``path`` as a string
    """
    with open(os.path.join(os.path.dirname(__file__), *path), 'rb') as f:
        return f.read().decode('UTF-8')

setup(
    name='flea',
    version=get_version(),
    description="Test WSGI applications",
    long_description=read('README.txt') + '\n\n' + read('CHANGELOG.txt'),
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Topic :: Internet :: WWW/HTTP :: WSGI',
        'Topic :: Software Development :: Testing',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.3',
    ],
    keywords='',
    author='Oliver Cope',
    author_email='oliver@redgecko.org',
    url='http://ollycope.com/software/flea/',
    license='BSD',
    packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'fresco>=0.3.0',
        'lxml',
        'cssselect',
        # -*- Extra requirements: -*-
    ],
    entry_points="""
    # -*- Entry points: -*-
    """,
)
