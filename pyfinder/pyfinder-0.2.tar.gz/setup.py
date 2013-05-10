from distutils.core import setup

setup(
    name = 'pyfinder',
    version = '0.2',
    description  = 'Look for files and text inside files',
    long_description = open('README').read(),
    py_modules = ['pyfinder'],
    author = 'Marco Buttu',
    author_email = "marco.buttu@gmail.com",
    license = 'BSD',
    url = 'https://pypi.python.org/pypi/pyfinder/',
    keywords = 'python generators distutils',
    scripts = ['scripts/pyfinder'],
    platforms = 'all',
    classifiers = [
        'Intended Audience :: Education',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3.3',
        'Topic :: Documentation',
        'Topic :: Education :: Testing',
        'Topic :: Text Processing :: Filters',
        'Topic :: Utilities'
   ],
)

