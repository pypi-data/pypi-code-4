from distutils.core import setup

setup(
    name='dcu.active-memory',
    version='0.1.1',
    author='Dirk Uys',
    author_email='dirkcuys@gmail.com',
    packages=['dcu.active-memory'],
    scripts=['bin/rotatefolder.py'],
    url='https://github.com/dirkcuys/active-memory',
    license='LICENSE.txt',
    description='Script rotate backup files on AWS S3 according to a grandfather, father, sun strategy.',
    long_description=open('README.md').read(),
    install_requires=[
        "boto >= 2.8.0",
    ],
)
