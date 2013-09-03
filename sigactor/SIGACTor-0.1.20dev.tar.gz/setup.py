from distutils.core import setup

import codecs 
try: 
    codecs.lookup('mbcs') 
except LookupError: 
    ascii = codecs.lookup('ascii') 
    func = lambda name, enc=ascii: {True: enc}.get(name=='mbcs') 
    codecs.register(func) 

setup(
    name='SIGACTor',
    version='0.1.20dev',
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
        'python-dateutil',
        'pyyaml'
    ],
)
