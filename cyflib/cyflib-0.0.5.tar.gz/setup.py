from distutils.core import setup
long_desc = open("cyflib/long_desc.txt").read()
setup(
    name='cyflib',
    version='0.0.5',
    author='inobagger',
    author_email='inobagger@gmail.com',
    packages=['cyflib', 'cyflib/ecdsa'],
    data_files=[('txt', ['cyflib/readme.txt', 'cyflib/license.txt', 'cyflib/changes.txt', 'cyflib/long_desc.txt'])],
    url='http://cyfnet.com/cyflib',
    license='Creative Commons Attribution 3.0 Unported License',
    description='CyfNet Python Library',
    download_url='http://pypi.python.org/pypi/cyflib',
    long_description=long_desc
)
