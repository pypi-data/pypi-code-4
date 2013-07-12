from setuptools import setup
# a workaround for a gross bug: http://bugs.python.org/issue15881#msg170215
try: 
    import multiprocessing
except ImportError: 
    pass
    
setup(
    name="renderwith",
    version="0.0.1",
    py_modules=['renderwith'],
    license = "LGPL",
    description = "engine-less html generation from python",
    long_description="""
Render html stright from python without involving another language or 'engine'.
Sometimes, you just don't want to involve these constructs just to generate some html.

Note: this renderer generates ugly, invalid html. 
It's only good for quick'n'dirty personal reporting.  
For externally visible documents, use one of the many production worthy templating engines.

### Usage
     with r.Table():
         for k,v in data.items():
             with r.Tr():
                 with r.Td():
                     r.text(k)
                 with r.Td():
                     r.text(v)
""",
    author = "tengu",
    author_email = "karasuyamatengu@gmail.com",
    url = "https://github.com/tengu/py-renderwith",
    classifiers = [
        "License :: OSI Approved :: GNU Library or Lesser General Public License (LGPL)",
        "Environment :: Console",
        "Programming Language :: Python",
        "Development Status :: 3 - Alpha",
        "Topic :: Utilities", 
        ],
    install_requires=[],
    test_suite='nose.collector',
    tests_require=['nose'],
)
