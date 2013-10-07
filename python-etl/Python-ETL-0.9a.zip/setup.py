from distribute_setup import use_setuptools
use_setuptools()

from setuptools import setup, find_packages
setup(
    name = "Python-ETL",
    version = "0.9a",
    packages = find_packages(),
    setup_requires=["hgtools"],

    # Project uses reStructuredText, so ensure that the docutils get
    # installed or upgraded on the target machine
    install_requires = ['xlrd==0.7.2', 'xlutils>=1.5.2', 'xlwt>=0.7.4', 'pyyaml>=3.10',
                        'docutils>=0.3', 'pyodbc>=2.1.11', 'pymongo>=2.3', 'mysql-python'],

    package_data = {
        # If any package contains *.txt or *.rst files, include them:
        '': ['*.txt', '*.rst', '*.css_t', 'csharp.config', '*.dll'],
        # And include any *.msg files found in the 'hello' package, too:
        'cardsharp': ['drivers/spss/64/*.dll', 'drivers/spss/i386/*.dll'],
    },

    # metadata for upload to PyPI
    author = "Original: Chris Bergstresser, Current: Michael Jugovich",
    author_email = "jugovich-michael@norc.org",
    description = "Python-ETL is an open-source Extract, Transform, load (ETL) library written in Python. It allows data to be read from a variety of formats and sources, where it can be cleaned, merged, and transformed using any Python library and then finally saved into all formats python-ETL supports. Ported from cardsharp by Chris Bergstresser.",
    license = "MIT",
    keywords = "python-etl, excel, spss, sas, extract, transform, load, text, mysql, mssql,",
    url = "http://python-etl.norc.org",

    # could also include long_description, download_url, classifiers, etc.
)