from distutils.core import setup

setup(
    name = "mercilessming",
    version = "0.0.8",
    description = "A minimalistic python dict model for mongodb",
    author = "Roi Avinoam",
    author_email = "roi@win.com",
    url = "https://github.com/win-social/mercilessming",
    py_modules = [ "mercilessming" ],
    requires = [ "pymongo" ],
    license = "MIT"
)