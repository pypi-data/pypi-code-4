from setuptools import setup, find_packages



requires = [
    'lockfile==0.8',
    'python-daemon',
    'ConfigParser',
    'requests',
    'pyelasticsearch',
    ]

setup(
    name = "LBIndex",
    version = "0.1.0",
    description = "Indexer Daemon for the neo-lightbase service",
    author = "Lightbase",
    author_email = "pedro.ricardo@lightbase.com.br",
    keywords = "index elasticsearch lightbase daemon",
    url = "",
    install_requires=requires,
    license = "GPLv2",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "Environment :: No Input/Output (Daemon)",
        "License :: OSI Approved :: GNU General Public License v2 (GPLv2)",
        "Natural Language :: Portuguese (Brazilian)",
        "Programming Language :: Python :: 2.7",
        "Topic :: Database :: Database Engines/Servers",

    ]
)