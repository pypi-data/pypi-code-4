import sys
try:
    import multiprocessing, logging
except ImportError:
    print "A more recent version of Python is needed."
    sys.exit(1)
try:
    from setuptools import setup, find_packages
except ImportError:
    try:
        from ez_setup import use_setuptools
    except ImportError:
        print("Can't find ez_setup")
        print("Try: wget http://peak.telecommunity.com/dist/ez_setup.py")
        sys.exit(1)
    use_setuptools()
    from setuptools import setup, find_packages


setup(
    name = 'HearPlanetAPI',
    version = '0.1.1',
    description = 'HearPlanet API driver',
    long_description = open('README.rst').read(),
    keywords = 'HearPlanet API driver',
    url = 'http://pypi.python.org/pypi/HearPlanetAPI/',
    author = 'Liam Kirsher',
    author_email = 'liam@hearplanet.com',
    zip_safe = True,

    packages = find_packages(exclude=['tests', 'examples']),
    include_package_data = True,
    exclude_package_data = {'': ['.gitignore']},
    data_files = [('/etc/', ['cfg/hearplanet.cfg'])],
    install_requires = [ 'requests', ],
    setup_requires = [ 'setuptools_git >= 0.3', ],

    tests_require = ['nose'],
    test_suite = 'nose.collector',

    classifiers = [
        'Development Status :: 3 - Alpha',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Natural Language :: English',
        'Programming Language :: Python',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
)
