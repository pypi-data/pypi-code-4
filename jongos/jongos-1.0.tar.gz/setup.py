from distutils.core import setup

setup(name = "jongos",
    version="1.0",
    description="JSON in-memory-db query engine. Insert, Find, Group and Count any JSON items with mongo based query.",
    author="Judotens Budiarto",
    author_email="judotens@gmail.com",
    license="three-clause BSD",
    url="https://github.com/judotens/jongos",
    long_description=__doc__,
    classifiers = [
        "Programming Language :: Python",
        "License :: OSI Approved :: BSD License",
        "Intended Audience :: Developers",
        "Topic :: Database" ],
    py_modules=['jongos'])
