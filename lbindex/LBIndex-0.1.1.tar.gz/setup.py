from setuptools import setup, find_packages



requires = [
    'lockfile==0.8',
    'python-daemon==1.5.4',
    'ConfigParser',
    'requests',
    'pyelasticsearch',
    ]

setup(
    name = "LBIndex",
    version = "0.1.1",
    author = "Lightbase",
    author_email = "pedro.ricardo@lightbase.com.br",
    url = "#",
    description = "Indexer Daemon for the neo-lightbase service",
    license = "GPLv2",
    keywords = "index elasticsearch lightbase daemon",
    install_requires=requires,
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