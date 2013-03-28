from setuptools import setup

setup(
    name='mozpoolclient',
    version='0.1.3',
    author='Zambrano, Armen',
    author_email='armenzg@mozilla.com',
    packages=['mozpoolclient'],
    scripts=[],
    url='http://pypi.python.org/pypi/mozpoolclient/',
    license='MPL',
    description='It allows you to interact with devices managed by Mozpool.',
    long_description=open('README.txt').read(),
    install_requires=[
        'requests >= 1.0.0',
    ],
)
