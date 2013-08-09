'''
Created on 15 Feb 2013

@author: plish
'''

import os
from distutils.core import setup

def read(filename):
    return open( os.path.join( os.path.dirname(__file__), filename)).read()

setup( 
        name = 'Trolly',
        version = '0.1.2',
        author = 'plish',
        author_email = 'plish.development@gmail.com',
        url = 'https://github.com/plish/Trolly',
        packages = ['trolly'],
        license = 'LICENCE.txt',
        requires = ['httplib2'],
        description = 'Trello API Wrapper',
        long_description = 'For more detail please refer to github page'
    )
