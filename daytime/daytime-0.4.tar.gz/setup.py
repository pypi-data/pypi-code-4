import os
from distutils.core import setup

VERSION = "0.4"

setup(
    name = "daytime", 
    version = VERSION, 
    author = "Thomas Leichtfuss", 
    author_email = "thomaslfuss@gmx.de",
    url = "https://github.com/thomst/daytime",
    download_url = "https://pypi.python.org/packages/source/d/daytime/daytime-{version}.tar.gz".format(version=VERSION),
    description = 'Extension for datetime.time with the main focus on comarison an making sums.',
    long_description = open('README.rst').read() if os.path.isfile('README.rst') else str(),
    py_modules = ["daytime"],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License (GPL)',
        'Operating System :: MacOS :: MacOS X',
        'Operating System :: Microsoft :: Windows',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python :: 2.7',
    ],
    license='GPL',
    keywords='datetime time daytime comparison',
)
