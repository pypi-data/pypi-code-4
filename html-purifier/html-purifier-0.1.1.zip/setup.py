from distutils.core import setup

setup(
    name = "html-purifier",
    version = "0.1.1",
    packages = ["purifier"],
    url = 'https://github.com/PixxxeL/python-html-purifier',
    author = 'pixel',
    author_email = 'ivan.n.sergeev@gmail.com',
    maintainer = 'pixel',
    maintainer_email = 'ivan.n.sergeev@gmail.com',
    license = 'GPL3',
    description = 'Cuts the tags and attributes from HTML that are not in the whitelist. Their content is leaves.',
    download_url = 'https://github.com/PixxxeL/python-html-purifier/archive/master.zip',
    classifiers = [
        'Operating System :: OS Independent',
        'Programming Language :: Python',
    ],
    #data_files = ['test-data\*.html'],
)
