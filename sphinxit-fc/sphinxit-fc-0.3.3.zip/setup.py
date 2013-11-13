import codecs
from os import path
from setuptools import setup, find_packages


read = lambda filepath: codecs.open(filepath, 'r', 'utf-8').read()


setup(
    name='sphinxit-fc',
    version='0.3.3',
    author='Future Colors (fork), Roman Semirook (original)',
    author_email='info@futurecolors.ru',
    packages=find_packages(),
    license='BSD',
    url='https://github.com/futurecolors/sphinxit',
    description='Lite and powerful SphinxQL query constructor',
    long_description=read(path.join(path.dirname(__file__), 'README.rst')),
    tests_require=[
        'nose >= 1.2',
        'unittest2',
    ],
    install_requires=[
        "six >= 1.1.0",
        "oursql >= 0.9.3",
    ],
    test_suite='nose.collector',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
)
