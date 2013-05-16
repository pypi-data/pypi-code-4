from os.path import dirname, join

from setuptools import setup, find_packages



version = '0.1'

README = join(dirname(__file__), 'README.md')
HISTORY = join(dirname(__file__), 'HISTORY.md')
LICENSE = join(dirname(__file__), 'LICENSE')

LONG_DESCRIPTION = open(README).read() + '\n\n' + \
        open(HISTORY).read() + '\n\n' + \
        '\n'.join(['> '+ line for line in open(LICENSE).readlines()])

setup(
    name = 'django-profiling',
    version = version,
    description = "Django Profiling",
    long_description = LONG_DESCRIPTION,
    classifiers = [
        "Framework :: Django",
        "Development Status :: 4 - Beta",
        #"Development Status :: 5 - Production/Stable",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "License :: OSI Approved :: Apache Software License"],
    keywords = 'django profiling',
    author = 'Texas A&M University, College of Architecture',
    author_email = 'webadmin@arch.tamu.edu',
    url = 'https://github.com/TAMUArch/django-profiling',
    packages = find_packages(),
    include_package_data = True,
    zip_safe = False,
    install_requires = [
        'setuptools',
        'django>=1.5'
    ]
)
