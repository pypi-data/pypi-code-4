from setuptools import setup

setup(
    name='pyoauth2-shift',
    version='0.0.1',
    author='GraphEffect, Inc.',
    author_email='nate@grapheffect.com',
    packages=['pyoauth2_shift', 'pyoauth2_shift.tests'],
    scripts=[],
    url='https://github.com/Songbee/pyoauth2',
    license='LICENSE.txt',
    description='OAuth 2.0 compliant client and server library.',
    long_description=open('README.txt').read(),
    install_requires=[
        "requests >= 0.14",
        "PyCrypto >= 2.6"
    ]
)
