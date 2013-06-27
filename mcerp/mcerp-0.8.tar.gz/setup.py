from distutils.core import setup

with open('README.txt') as file:
    long_description = file.read()

setup(name='mcerp',
    version='0.8',
    author='Abraham Lee',
    description='Real-time Monte Carlo, Latin-Hypercube Sampling-based, Error Propagation',
    author_email='tisimst@gmail.com',
    url='http://pypi.python.org/pypi/mcerp',
    license='BSD License',
    long_description=long_description,
    package_dir={'mcerp':''},
    packages=['mcerp'],
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Education',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.0',
        'Programming Language :: Python :: 3.1',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Topic :: Education',
        'Topic :: Scientific/Engineering',
        'Topic :: Scientific/Engineering :: Mathematics',
        'Topic :: Scientific/Engineering :: Physics',
        'Topic :: Software Developement',
        'Topic :: Software Developement :: Libraries',
        'Topic :: Software Developement :: Libraries :: Python Modules',
        'Topic :: Utilities'
        ]
    )
