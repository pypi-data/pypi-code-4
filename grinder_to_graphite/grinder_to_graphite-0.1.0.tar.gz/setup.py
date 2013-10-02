from setuptools import setup

setup(
    name='grinder_to_graphite',
    version='0.1.0',
    author='Travis Bear',
    author_email='travis_bear@yahoo.com',
    keywords = "graphite grinder logster logs",
    packages=[
        'g2g',
        'g2g.aggregator',
        'g2g.logtype',
        'g2g.logtype.grinder'],
    scripts=['bin/g2g',],
    url='https://grinder_to_graphite.readthedocs.org/en/latest/',
    license='LICENSE.txt',
    description='Ingests data from Grinder logs into Graphite where it can be visualized.',
    long_description=open('README.txt').read(),
    install_requires=[
        "mtFileUtil",
        "pygtail",
        "pyyaml"]
)
