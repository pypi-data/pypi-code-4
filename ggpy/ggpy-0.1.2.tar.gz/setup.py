from setuptools import setup, find_packages

setup(
    name         = 'ggpy',
    version      = '0.1.2',
    author       = 'Sammy Nammari, Daniel Duckworth',
    author_email = 'sammy.nammari@gmail.com, duckworthd@gmail.com',
    description  = 'ggplot2 from your command line',
    license      = 'BSD',
    keywords     = 'plot visualization plotting ggplot2',
    url          = 'http://github.com/premisedata/ggpy',
    packages     = find_packages(),
    classifiers  = [
      'Development Status :: 4 - Beta',
      'Intended Audience :: Science/Research',
      'Intended Audience :: System Administrators',
      'License :: OSI Approved :: BSD License',
      'Programming Language :: Python',
      'Topic :: Scientific/Engineering :: Visualization',
      'Operating System :: Unix',
      'Operating System :: MacOS',
    ],
    install_requires = [
      'numpy>=1.7.1',
      'pandas>=0.11.0',
    ],
    entry_points = {
      'console_scripts': [
        'ggpy = ggpy.plot:main'
      ]
    }
)
