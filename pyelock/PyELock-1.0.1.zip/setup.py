from distutils.core import setup

setup(
    name='PyELock',
    version='1.0.1',
    author='Nitzan Miron',
    author_email='nitzanm@gmail.com',
    packages=['pyelock'],
    url='http://pypi.python.org/pypi/PyELock/',
    license='LICENSE.txt',
    description='Pure Python wrapper for elock distributed locking server.',
    long_description=open('README.txt').read(),
    install_requires=[],
)