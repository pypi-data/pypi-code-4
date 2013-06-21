from setuptools import setup, Extension
# a workaround for a gross bug: http://bugs.python.org/issue15881#msg170215
try: 
    import multiprocessing
except ImportError: 
    pass

setup(
    name='ikedarts',
    version='0.1',
    ext_modules=[Extension("_ikedarts", 
                           ["_ikedarts.c",
                            "ikedarts-c/ikedarts.cpp"
                            ])],
    include_dirs=["ikedarts-c"],

    #scripts = ["yoyodyne.py"],
    entry_points={"console_scripts": [ 'ikedarts=ikedarts:main' ]},

    packages=['ikedarts'],

    license = "LGPL",
    description = "python wrapper for darts",
    long_description=file('README.rst').read(),
    author = "tengu",
    author_email = "karasuyamatengu@gmail.com",
    url = "https://github.com/tengu/ikedarts",

    test_suite='nose.collector',
    tests_require=['nose'],
)
