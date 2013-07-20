from distutils.core import setup

VERSION = '0.8.1'

def read_readme():
    with open('README.rst') as file:
        return file.read()

classifiers = [
    "Programming Language :: Python",
    
    "Development Status :: 4 - Beta",
    
    "Environment :: Console",
        
    "License :: OSI Approved :: MIT License",
    
    "Operating System :: OS Independent",
    
    "Topic :: Database",
    "Topic :: Scientific/Engineering :: Information Analysis",
    ]

setup(
    version = VERSION,
    name = 'Ax_FuzzyTourney',
    packages = [
        'axonchisel',
        'axonchisel.fuzzytourney',
        'axonchisel.fuzzytourney.config',
        'axonchisel.fuzzytourney.contrib',
    ],
    url = "https://bitbucket.org/dkamins/ax_fuzzytourney/",
    description = "Fuzzy Tournament - Big Data Heuristic Programmable Reducing Miner.",
    author = "Dan Kamins",
    author_email = "dos@axonchisel.net",
    keywords = ["data mining", "big data", "map/reduce", "heuristics", "analytics", "business intelligence", "audit", "programmable"],
    requires = ["PyYAML"],
    license = "MIT",
    classifiers = classifiers,
    long_description = read_readme(),
)


