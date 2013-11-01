from distutils.core import setup

setup(
    name='SimplePake',
    version='0.1',
    author='woshifyz',
    author_email='zhouzhen912@gmail.com',
    packages=['pake'],
    scripts=['bin/pake'],
    url='http://pypi.python.org/pypi/Pake/',
    license='LICENSE.txt',
    description='python task runner',
    long_description=open('README.txt').read(),
)
