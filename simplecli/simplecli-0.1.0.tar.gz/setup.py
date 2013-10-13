"""
simplecli
--------------

A set of utilities for writing command line interfaces with ease.

Links
`````

* `documentation <http://simplecli.readthedocs.org>`_


"""
import sys
from setuptools import setup

# Hack to prevent stupid TypeError: 'NoneType' object is not callable error on
# exit of python setup.py test # in multiprocessing/util.py _exit_function when
# running python setup.py test (see https://github.com/pypa/virtualenv/pull/259)
try:
    import multiprocessing
except ImportError:
    pass

import simplecli

install_requires = []
if sys.version_info < (2, 7):
    install_requires += ['argparse']

setup(
    name='simplecli',
    version=simplecli.__version__,
    url='http://github.com/baeuml/simplecli',
    license='BSD',
    author='Dan Jacob, Sean Lynch, Martin Baeuml',
    author_email='danjac354@gmail.com, techniq35@gmail.com, baeuml@gmail.com',
    description='Makes writing command line interfaces simple',
    long_description=__doc__,
    packages=[
        'simplecli'
    ],
    test_suite='nose.collector',
    zip_safe=False,
    platforms='any',
    install_requires=install_requires,
    tests_require=[
        'nose',
    ],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ]
)
