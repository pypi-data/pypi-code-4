from distutils.core import setup

setup(
    name='pypb',
    version='1.0.0',
    author='Trey Stout',
    author_email='treystout@gmail.com',
    packages=['pypb', 'pypb.test'],
    scripts=[],
    url='http://pypi.python.org/pypi/pypb/',
    license='LICENSE.txt',
    description='console-based progress bar',
    long_description=open('README.txt').read()
)
