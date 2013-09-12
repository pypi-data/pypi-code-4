from distutils.core import setup

setup(
    name='TrelloCardUpdate',
    version='0.0.1',
    author='Thomas Ballinger',
    author_email='tom@hackerschool.com',
    packages=['trellocardupdate'],
    scripts=['bin/tu.py', 'bin/tu'],
    license='LICENSE.txt',
    description='basic command line trello client',
    long_description=open('README.txt').read(),
)


