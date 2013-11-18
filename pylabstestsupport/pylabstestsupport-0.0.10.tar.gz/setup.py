from setuptools import setup

setup(
    name='pylabstestsupport',
    version='0.0.10',
    author='Michael Heyvaert',
    author_email='release.management@amplidata.com',
    packages=['pylabstestsupport'],
    url='http://pypi.python.org/pypi/pylabstestsupport',
    license='LICENSE.txt',
    description='Support for testing pylabs3 code',
    long_description='',#open('README.txt').read(),
    install_requires=[
        "mock >= 1.0.1"
    ]
)
