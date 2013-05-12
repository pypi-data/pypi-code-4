import os
from setuptools import setup, find_packages

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name = "firstdjango",
    version = "1.0",
    url = 'http://akasig.org',
    license = 'AGPL',
    description = "My first Django app",
    long_description = read('README'),
    author = 'Jean Millerat',
    author_email = 'sig@akasig.org',
    packages = find_packages('src'),
    package_dir = {'': 'src'},
    install_requires = ['distribute'],
    classifiers = [
        'Development Status :: 1 - Planning',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU Affero General Public License v3 or later (AGPLv3+)',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP',
    ]
)
