import re

from setuptools import setup
from os.path import join, dirname


version = re.search("__version__ = '([^']+)'", open(
        join(dirname(__file__), 'scrapyredirect.py')
        ).read().strip()).group(1)

setup(
    name='scrapy-redirect',
    version=version,
    license=open('LICENSE.txt').readline().strip(),
    description='Restrict authorized Scrapy redirections to the website start_urls',
    long_description=open('README.txt').read(),
    author='Balthazar Rouberol',
    author_email='balthazar@mapado.com',
    url='http://github.com/mapado/scrapy-redirect',
    keywords="scrapy crawl scraping",
    py_modules=['scrapyredirect'],
    platforms = ['Any'],
    install_requires = ['scrapy>=0.16'],
    classifiers = [
        'Development Status :: 4 - Beta',
        'Environment :: No Input/Output (Daemon)',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python'
        ]
)