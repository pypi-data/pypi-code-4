from os.path import dirname, join
from setuptools import setup

def slurp(fname):
    path = join(dirname(__file__), fname)
    with open(path) as f:
        f.read()

setup(
    name='php-reference',
    version='0.0.1',
    author='Stuart Campbell',
    author_email='stuart@harto.org',
    description='A CLI command for fetching PHP documentation',
    long_description=slurp('README.rst'),
    license='MIT',
    keywords='php reference documentation cli',
    url='https://github.com/harto/php-reference',
    classifiers=['Development Status :: 3 - Alpha'],

    packages=['php_reference'],

    install_requires=['beautifulsoup4==4.1.1',
                      'html2text==3.200.3'],

    entry_points={
        'console_scripts': [
            'php-reference=php_reference:main',
        ],
    },
)
