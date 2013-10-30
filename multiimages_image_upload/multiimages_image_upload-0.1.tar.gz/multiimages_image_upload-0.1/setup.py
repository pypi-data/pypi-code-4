# setup.py file
from setuptools import setup, find_packages
setup(
    name = "multiimages_image_upload",
    version = "0.1",
    py_modules = ['multiimages_upload',],

    install_requires = ['easy-thumbnails',],

    package_data = {
        # If any package contains *.txt or *.rst files, include them:
        '': ['README','*.txt', '*.rst'],
    },

    # metadata for upload to PyPI
    author = "yogesh dwivedi",
    author_email = "yogeshd.mca@gmail.com",
    description = "Multiimages image upload",
    license = "BSD",
    keywords = "multiimages image upload",
    url = "",
    long_description = "",
    platforms=['any'],
    download_url='',
)
