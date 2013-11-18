"""Setup file for AtmosphericChemistry package"""
from distutils.core import setup

setup(
    name = 'AtmosphericChemistry',
    version = '0.1.0',
    author = 'M. G. Schultz',
    author_email = 'm.schultz@fz-juelich.de',
    packages = ['ac', 'ac.gasphase', 'ac.gasphase.test', 'ac.utils'],
    package_data = {'ac': ['testdata/*', 'gasphase/data/*']},
    scripts = ['bin/check_mass.py', 'bin/convert_moz_mim2.py', 
               'bin/extract_photo_reactions.py', 
               'bin/prepare_hammoz.py', 'bin/prepare_mecca.py', 
               'bin/test_reaction.py', 'bin/test_translate.py'
              ],
    url = 'http://pypi.python.org/pypi/AtmosphericChemistry/',
    license = 'LICENSE.txt',
    description = 'Tools for creating and managing atmospheric chemistry mechanisms.',
    long_description = open('README.txt').read(),
    classifiers = ['Intended Audience :: Science/Research',
                    'Development Status :: 3 - Alpha',
                    'License :: OSI Approved :: MIT License',
                    'Programming Language :: Python :: 2.7',
                    'Topic :: Scientific/Engineering :: Atmospheric Science',
                    'Operating System :: MacOS',
                    'Operating System :: Microsoft :: Windows',
                    'Operating System :: Unix',
                  ],
    install_requires = ["numpy"],
)
