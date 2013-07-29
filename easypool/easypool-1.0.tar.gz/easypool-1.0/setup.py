from distutils.core import setup

setup(
    name='easypool',
    version='1.0',
    packages=['easypool',],
    license='GPLv2',
    long_description=open('README.md').read(),
    author='Robert Labonte',
    author_email='rlabonte@gmail.com',
    url='https://github.com/RobertLabonte/easypool',
    download_url='https://github.com/RobertLabonte/easypool/tarball/0.1',
    keywords = ['threads', 'threading', 'queue', 'threadpool'],
)
