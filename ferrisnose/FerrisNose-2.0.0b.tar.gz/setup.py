from setuptools import setup

VERSION = '2.0.0b'

setup(
    name="FerrisNose",
    version=VERSION,
    author='Jon Parrott',
    author_email='jjramone13@gmail.com',
    maintainer='Jon Parrott',
    maintainer_email='jjramone13@gmail.com',
    description='nose plugin for bootstrapping the GAE SDK and GAE Testbed for the Ferris Framework',
    url='https://bitbucket.org/jonparrott/ferris-nose',
    license='Apache License 2.0',
    classifiers=[
        'Development Status :: 4 - Beta',
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python',
    ],
    entry_points={
        'nose.plugins.0.10': [
            'ferris = ferrisnose:FerrisNose'
        ]
    },
    py_modules=['ferrisnose'],
    install_requires=['nose>=0.10.1'],
)
