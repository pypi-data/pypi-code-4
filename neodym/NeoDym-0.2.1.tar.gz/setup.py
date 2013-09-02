from distutils.core import setup

setup(
    name='NeoDym',
    version='0.2.1',
    author='Brian Wiborg',
    author_email='baccenfutter@c-base.org',
    packages=['neodym'],
    scripts=[],
    url='http://pypi.python.org/pypi/NeoDym/',
    license='LICENSE.txt',
    description='A thin message-bus wrapper around asyncore.',
    long_description=open('README.txt').read(),
    install_requires=[],
)

