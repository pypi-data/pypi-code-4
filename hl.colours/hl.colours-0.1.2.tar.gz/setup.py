from setuptools import setup, find_packages


with open('README.rst') as f:
    long_description = f.read()


setup(
    name="hl.colours",
    version="0.1.2",
    packages=find_packages(),
    description="A simple way to add colours to terminal output in Python.",
    long_description=long_description,
    author="Hing-Lung Lau",
    author_email="lung220@gmail.com",
    url="http://github.com/hllau/hl.colours",
    license="Apache v2",
    keywords="color colour terminal command line output",
    classifiers = [ 
    'Environment :: Web Environment',
    'Intended Audience :: Developers',
    'Programming Language :: Python :: 2.7',
    'Topic :: Software Development :: Libraries :: Python Modules',
    'License :: OSI Approved :: Apache Software License',
    ]
)

