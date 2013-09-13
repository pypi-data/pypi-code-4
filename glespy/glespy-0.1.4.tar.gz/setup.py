from distutils.core import setup
import os

if os.path.exists('README.txt'):
    long_description = open('README.txt').read()

setup(
    name='glespy',
    version='0.1.4',
    packages=['glespy', 'glespy.test', 'glespy.tools', 'glespy.tools.test', 'glespy.test_data'],
    url='https://pypi.python.org/pypi/glespy/',
    # license='no license yet...',
    author='yarnaid',
    author_email='yarnaid@gmail.com',
    description='Bindings for GLESP for calculations with spherical harmonics',
    keywords='GLESP bindings',
    long_description=long_description,
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Topic :: Utilities",
        "Intended Audience :: Science/Research",
        "License :: Freeware",
        "Natural Language :: Russian",
        "Operating System :: POSIX :: Linux",
        "Programming Language :: Python :: 2",
        "Topic :: Scientific/Engineering :: Astronomy",
    ],
)
