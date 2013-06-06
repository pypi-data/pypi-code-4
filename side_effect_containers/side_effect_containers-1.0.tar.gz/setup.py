from setuptools import setup

setup(
    name='side_effect_containers',
    version='1.0',
    author='Josh Matthias',
    author_email='jmatthias4570@gmail.com',
    packages=['side_effect_containers'],
    scripts=[],
    url='https://github.com/jmatthias/side_effect_containers',
    license='LICENSE.txt',
    description=(
        'Containers that do a side-effect when an item is added or removed.'
        ),
    long_description=open('README_pypi.txt').read(),
    install_requires=[
        ],
    )