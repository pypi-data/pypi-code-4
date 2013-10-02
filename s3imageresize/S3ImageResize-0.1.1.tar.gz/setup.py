from distutils.core import setup

setup(
    name='S3ImageResize',
    version='0.1.1',
    author='Dirk Uys',
    author_email='dirk@p2pu.org',
    packages=['s3imageresize'],
    scripts=['bin/s3imageresize.py'],
    url='http://pypi.python.org/pypi/s3imageresize/',
    license='LICENSE.txt',
    description='Script to resize images on S3.',
    long_description=open('README.md').read(),
    install_requires=[
        "Pillow >= 2.1.0",
        "boto >= 2.8.0",
    ],
)
