from distutils.core import setup

setup(
    name='EPN',
    version='0.1.0',
    author='Marco S. Nobile',
    author_email='nobile@disco.unimib.it',
    packages=['epn'],
    scripts=[''],
    url='http://pypi.python.org/pypi/EPN/',
    license='LICENSE.txt',
    description='Evolutionary Petri Nets.',
    long_description=open('README.txt').read(),
    install_requires=[
        "pydot >= 1.0.28",
        "graphviz >= 2.26.3",
        "pyparsing == 1.5.7"
    ],
)