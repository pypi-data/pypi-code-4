import os

from setuptools import setup, find_packages


root = os.path.abspath(os.path.dirname(__file__))
path = lambda *p: os.path.join(root, *p)


setup(
    name='pyLibrary',
    version="0.1.13316",
    description='Library of Wonderful Things',
    long_description=open(path('README.txt')).read(),
    author='Kyle Lahnakoski',
    author_email='kyle@lahnakoski.com',
    url='https://github.com/klahnakoski/pyLibrary',
    license='MPL 2.0',
    packages=['util'],
    install_requires=['pymysql', 'requests'],
    include_package_data=True,
    zip_safe=False,
    classifiers=[  #https://pypi.python.org/pypi?%3Aaction=list_classifiers
        "Development Status :: 2 - Pre-Alpha",
        "Topic :: Software Development :: Libraries",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "License :: OSI Approved :: Mozilla Public License 2.0 (MPL 2.0)",
    ]
)
