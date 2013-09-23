# initdotpy.fluent
# Matchers and Stubs for mock.
# Copyright (C) 2012 Andrew Burrows
# E-mail: burrowsa AT gmail DOT com

# initdotpy 0.0.1
# https://github.com/burrowsa/initdotpy

# Released subject to the BSD License
# Please see https://github.com/burrowsa/initdotpy/blob/master/LICENSE.txt

if __name__ == "__main__":
    params = dict(name="initdotpy",
        version="0.0.2",
        description="Automates imports in __init__.py file",
        author="Andrew Burrows",
        author_email="burrowsa@gmail.com",
        url="https://github.com/burrowsa/initdotpy",
        packages=['initdotpy'],
        license="BSD",
        long_description="""The initdotpy library is designed to automatically import the contents of child modules/packages in a __init__.py file""",
        classifiers=["Development Status :: 2 - Pre-Alpha",
                     "Environment :: Console",
                     "Intended Audience :: Developers",
                     "License :: OSI Approved :: BSD License",
                     "Programming Language :: Python",
                     "Programming Language :: Python :: 2.7",
                     "Programming Language :: Python :: Implementation :: CPython",
                     "Operating System :: OS Independent",
                     "Topic :: Software Development :: Libraries",
                     "Topic :: Software Development :: Libraries :: Python Modules",
                     "Topic :: Software Development :: Testing"])

    try:
        from setuptools import setup
    except ImportError:
        from distutils.core import setup
    else:
        #params['install_requires'] = ['mock>=0.8.0']
        pass

    setup(**params)
