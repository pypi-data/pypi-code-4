from os.path import join, dirname
from setuptools import find_packages, setup


def get_file_contents(filename):
    with open(join(dirname(__file__), filename)) as fp:
        return fp.read()

setup(name='poolbase',
    version='0.1.1',
    description="A connection pool for anything",
    long_description=get_file_contents('README.rst'),
    author="duanhongyi",
    author_email="duanhongyi@doopai.com",
    url='https://github.com/duanhongyi/poolbase',
    packages=find_packages(),
    license="MIT",
    classifiers=(
          "License :: OSI Approved :: MIT License",
          "Topic :: Database",
          "Topic :: Software Development :: Libraries :: Python Modules",
    )
)
