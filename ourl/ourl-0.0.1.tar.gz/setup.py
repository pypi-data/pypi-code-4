from setuptools import setup
# a workaround for a gross bug: http://bugs.python.org/issue15881#msg170215
try: 
    import multiprocessing
except ImportError: 
    pass
    
setup(
    name="ourl",
    version="0.0.1",
    entry_points="""
    [console_scripts]
    ourl = ourl:main
    """,
    py_modules=['ourl'],
    license = "LGPL",
    description = "http client with oauth and pipelined processing",
    long_description="""
""",
    author = "tengu",
    author_email = "karasuyamatengu@gmail.com",
    url = "https://github.com/tengu/py-ourl",
    classifiers = [
        "License :: OSI Approved :: GNU Library or Lesser General Public License (LGPL)",
        "Environment :: Console",
        "Programming Language :: Python",
        "Development Status :: 3 - Alpha",
        "Topic :: Utilities", 
        ],

    install_requires='oauth2 baker'.split(),

    test_suite='nose.collector',
    tests_require=['nose'],
)
