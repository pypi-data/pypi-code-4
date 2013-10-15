import os
import re
import shutil
from os import path
from setuptools import setup

# parse version out of file
with open(path.join('configgen', 'version.py')) as srcFile:
    versionFile = srcFile.read()
    versionMatch = re.search(r"^__version__ = '([^']+)'", versionFile, re.MULTILINE)
    if versionMatch:
        packageVersion = versionMatch.group(1)
    else:
        raise RuntimeError('cannot find version string')

# read long_desc from README.rst, fall back to ../README.rst
# need to do silly things to get README in the root directory for parsing
# by source control while also getting distributed in the package
copyReadme = False
readmeName = 'README.rst'
readmeNameParent = path.join('..', readmeName)
for readme in (readmeName, readmeNameParent):
    try:
        with open(readme) as descFile:
            longDescription = descFile.read()
            break
    except IOError:
        pass
    copyReadme = True
else:
    raise IOError('cannot open readme file')

if copyReadme:
    shutil.copy(readme, '.')
    import atexit
    @atexit.register
    def cleanup():
        os.unlink(readmeName)

setup(
    name='configgen',
    version=packageVersion,
    author='wil paredes',
    author_email='configgen@dystedium.com',
    description='a noble script configgens the smallest app',
    long_description=longDescription,
    url='https://bitbucket.org/dystedium/configgen',
    packages=['configgen'],
    entry_points={
        'console_scripts':[
            'configgen = configgen.main:main'
        ]
    },
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2.7',
        'Topic :: Software Development :: Code Generators',
        'Topic :: Text Processing :: Markup',
        'Topic :: Utilities'
    ]
)
