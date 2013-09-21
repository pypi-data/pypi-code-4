try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

import crashlog

with open('README.md') as fo:
    long_description=fo.read()

setup(
    name='crashlog',
    version=crashlog.__version__,
    description='Log & email uncaught exceptions',
    long_description=long_description,
    author='Miki Tebeka',
    author_email='miki.tebeka@gmail.com',
    license='MIT',
    url='https://bitbucket.org/tebeka/crashlog',
    py_modules=['crashlog'],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 3',
        'Topic :: Software Development :: Libraries',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    tests_require=['nose'],
    test_suite = 'nose.collector',
)
