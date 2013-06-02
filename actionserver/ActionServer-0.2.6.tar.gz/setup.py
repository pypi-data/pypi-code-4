
from distutils.core import setup

setup(
    name='ActionServer',
    author='Josueh Machado',
    author_email='josueh.cg@gmail.com',
    version='0.2.6',
    packages=['action',],
    license='CC by Josueh',
)

''' INSTRUCTION FOR UPDATE PACKAGE:
    $ python setup.py sdist
    $ python setup.py register
    $ python setup.py sdist upload
'''
