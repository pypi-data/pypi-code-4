from setuptools import setup

setup(
    name='lcdapublictools',
    version='0.1.1',
    author='Josh Matthias',
    author_email='jmatthias4570@gmail.com',
    packages=['lcdapublictools'],
    scripts=[],
    url='https://github.com/jmatthias/lcdapublictools',
    license='LICENSE.txt',
    description=('Open source tools from Lacoda.'),
    long_description=open('README_pypi.txt').read(),
    install_requires=[
        'side_effect_containers',
        'SQLAlchemy',
        ],
    )