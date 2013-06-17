from distutils.core import setup

setup(
    name = "iso-8601",
    version = "0.2.4",
    description = "Flexible ISO 8601 parser: pass in a valid ISO 8601 string, and a datetime object will be returned.",
    url = "http://hg.schinckel.net/iso-8601/",
    author = "Matthew Schinckel",
    author_email = "matt@schinckel.net",
    packages = [
        "iso8601",
    ],
    classifiers = [
        'Programming Language :: Python',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Intended Audience :: Developers',
        'Development Status :: 4 - Beta',
        'Topic :: Software Development :: Libraries',
    ],
)
