from setuptools import setup, find_packages

with open('falafel/version.py') as f:
    for line in f:
        if line.startswith('__version__'):
            exec(line)

classifiers = [
    'License :: OSI Approved :: BSD License',
    'Operating System :: OS Independent',
    'Intended Audience :: Developers',
    'Intended Audience :: Science/Research',
    'Programming Language :: Python',
    'Programming Language :: Python :: 2',
    'Programming Language :: Python :: 2.7',
    'Programming Language :: Python :: 3',
    'Programming Language :: Python :: 3.3',
]

setup(
    author = 'Thomas Hisch',
    author_email = 't.hisch@gmail.com',
    classifiers = classifiers,
    description = ('Library suited for long-running unit/integration tests, '
                   'based on the unittest package'),
    name = "falafel",
    packages = find_packages(),
    platforms = 'Any',
    requires = ['python (>=2.7.0)',
                'pygments (>=1.6)',
                'tabulate (>=0.6)'],
    version = __version__
)
