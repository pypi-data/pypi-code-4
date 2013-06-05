from distutils.core import setup

setup(
    name='RemoteMoose',
    version='0.1.0',
    author='Michael Imelfort',
    author_email='mike@mikeimelfort.com',
    packages=['remotemoose', 'remotemoose.test'],
    scripts=['bin/remoteMoose'],
    url='http://pypi.python.org/pypi/RemoteMoose/',
    license='GPLv3',
    description='RemoteMoose',
    long_description=open('README.rst').read(),
    install_requires=["numpy >= 1.6.1",
                      "matplotlib >= 1.1.0"]
)
