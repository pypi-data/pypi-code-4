from distutils.core import setup

setup(
    name='ModemDriver',
    version='2.0.14',
    packages=['ModemDriver',],
    license='LGPL',
    long_description=open('README.txt').read(),
    url='http://rab.co.id/gsmmodem',
    author='Owo Sugiana',
    author_email='sugiana@rab.co.id',
    description='Modem driver using AT command',
)
