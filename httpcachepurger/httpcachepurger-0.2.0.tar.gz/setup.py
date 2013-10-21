from setuptools import setup

setup(
    name='httpcachepurger',
    version='0.2.0',
    author='Giacomo Bagnoli',
    author_email='info@asidev.com',
    packages=['httpcachepurger'],
    url='https://code.asidev.net/projects/httpcachepurger',
    license='LICENSE.txt',
    description='HTTP Cache purger client library',
    long_description=open('README.txt').read(),
    install_requires = [ ],
    test_suite = 'nose.collector',
    tests_require = [ "Nose", "coverage" ],
    classifiers  = [
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: Other/Proprietary License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Utilities"
    ],
    entry_points= {
        'console_scripts' : [
            'cpurger = httpcachepurger.cmdline:main'
        ]
    }
)
