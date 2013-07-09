from distutils.core import setup

setup(
    name='dt8601',
    version='0.2.0',
    author='Armin Hanisch',
    author_email='mail@arminhanisch.de',
    packages=['dt8601', 'dt8601.test'],
    url='http://pypi.python.org/pypi/dt8601/',
    license='LICENSE.txt',
    description='Useful date routines.',
    long_description=open('README.rst').read(),
)
