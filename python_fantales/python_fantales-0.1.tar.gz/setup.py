# fantales's setup.py
from setuptools import setup, find_packages
setup(
    name = "python_fantales",
    version = "0.1",
    py_modules = ['python_fantales'],

    package_data = {
        # If any package contains *.txt or *.rst files, include them:
        '': ['README','*.txt', '*.rst'],
    },

    # metadata for upload to PyPI
    author = "Sapna Jadon",
    author_email = "jadon.sapna11@gmail.com",
    description = "helps to visualise opinions of movie fans derived from a survey",
    license = "BSD",
    keywords = ["Html", "fans", "xml"],
    url = "",
    platforms=['any'],
    download_url='',
)
