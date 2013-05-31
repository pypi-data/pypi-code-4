
from distutils.core import setup
#from distutils.extension import Extension

version = '1.11'

setup(
    name='red-black-tree-mod',
    py_modules=[ 
        'red_black_set_mod', 'red_black_bag_mod', 
        'red_black_dict_mod', 'red_black_dupdict_mod', 
        ],
    version=version,
    description='Flexible python implementation of red black trees',
    long_description='''
A set of python modules implementing red black trees is provided.

Red-black trees are a little slower than treaps (some question this), but they give a nice
low standard deviation in operation times, and this code is quite flexible.

Modules are provided for red black trees that enforce uniqueness, and red black trees that allow duplicates.
They also allow for set-like use and dictionary-like use.

Much of the work here was done by Duncan G. Smith.  Dan just put some finishing touches on it.
''',
    author='Daniel Richard Stromberg',
    author_email='strombrg@gmail.com',
    url='http://stromberg.dnsalias.org/~strombrg/red-black-tree-mod/',
    platforms='Cross platform',
    license='MIT',
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 3",
        ],
    )


