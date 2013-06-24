from distutils.core import setup

setup(
    name='Souch',
    version='0.0.4',
    author='Victor M. Castillo',
    author_email='mini.guero@hotmail.com',
    packages=['souch', 'souch.utils'],
    scripts=['souch/souch.py'],
    url='https://github.com/Verurteilt/souch',
    license='LICENSE.txt',
    description='Simple CouchDB client for Python',
    long_description=open('README.txt').read(),
)
