from distutils.core import setup

with open('README.txt') as f:
    readme = f.read()

setup(
    name='clc',
    version='0.0.1',
    author='Phil Adams',
    author_email='phil@philadams.net',
    url='https://github.com/philadams/clc',
    license='LICENSE.txt',
    description='Simple charts on the command line from stdin or file',
    long_description=readme,
    packages=['clc'],
    scripts=['bin/clc'],
)

