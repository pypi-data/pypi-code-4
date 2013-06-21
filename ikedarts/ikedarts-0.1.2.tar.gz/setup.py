from setuptools import setup, Extension
# a workaround for a gross bug: http://bugs.python.org/issue15881#msg170215
try: 
    import multiprocessing
except ImportError: 
    pass

setup(
    name='ikedarts',
    version='0.1.2',
    ext_modules=[Extension("_ikedarts", 
                           ["_ikedarts.c",
                            "ikedarts-c/ikedarts.cpp",
                            "ikedarts-c/ikedarts_main.cpp",
                            ])],
    include_dirs=["ikedarts-c"],
    headers=["ikedarts-c/ikedarts.h"],

    #scripts = ["yoyodyne.py"],
    entry_points={"console_scripts": [ 'ikedarts=ikedarts:main' ]},

    packages=['ikedarts'],

    license = "LGPL",
    description = "Python interface to DARTS by Kudo Taku.",
    long_description="""
see http://chasen.org/~taku/software/darts/ for detaisl for darts.
see test for usage: ikedarts/tests/test.py
""",
    author = "tengu",
    author_email = "karasuyamatengu@gmail.com",
    url = "https://github.com/tengu/ikedarts",

    test_suite='nose.collector',
    tests_require=['nose'],
)
