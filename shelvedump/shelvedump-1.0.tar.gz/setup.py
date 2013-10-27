#!/usr/bin/env python
# coding: utf-8

from setuptools import setup


setup(
    name='shelvedump',
    url='https://github.com/miracle2k/shelvedump',
    version='1.0',
    license='BSD',
    author=u'Michael Elsdörfer',
    author_email='michael@elsdoerfer.com',
    description=
        'dump the content of a Python shelve database to JSON',
    py_modules=['shelvedump'],
    install_requires=['jsonpickle'],
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
    ],
    entry_points="""[console_scripts]\nshelvedump = shelvedump:run\n""",
)