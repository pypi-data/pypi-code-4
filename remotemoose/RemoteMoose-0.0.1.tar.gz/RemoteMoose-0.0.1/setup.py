from distutils.core import setup

setup(
    name='RemoteMoose',
    version='0.0.1',
    author='Michael Imelfort',
    author_email='mike@mikeimelfort.com',
    packages=['remotemoose', 'remotemoose.test'],
    scripts=['bin/RemoteMoose'],
    url='http://pypi.python.org/pypi/RemoteMoose/',
    license='GPLv3',
    description='RemoteMoose',
    long_description=open('README.rst').read(),
    install_requires=[],
)
