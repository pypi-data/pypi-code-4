from distutils.core import setup

setup(
    name='SIGACTor',
    version='0.1.02dev',
    description=open('README.txt').read(),
    url='http://bitbucket.org/davidystephenson/sigactor',
    author='David Y. Stephenson',
    author_email='david@davidystephenson.com',
    packages=['sigactor'],
    license='Proprietary',
    long_description=open('README.txt').read(),
    install_requires=[
        'beautifulsoup4',
        'feedparser',
    ],
)
