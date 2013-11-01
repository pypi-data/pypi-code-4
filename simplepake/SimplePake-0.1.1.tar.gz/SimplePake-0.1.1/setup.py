from distutils.core import setup

setup(
    name='SimplePake',
    version='0.1.1',
    author='woshifyz',
    author_email='zhouzhen912@gmail.com',
    packages=['pake'],
    scripts=['bin/pake'],
    url='https://github.com/woshifyz/pake',
    license='LICENSE.txt',
    description='Python Task Runner',
    long_description=open('README.txt').read(),
)
