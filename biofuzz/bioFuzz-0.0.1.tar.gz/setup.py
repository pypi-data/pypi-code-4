from distutils.core import setup

setup(
    name='bioFuzz',
    version='0.0.1',
    author='Michael Imelfort',
    author_email='mike@mikeimelfort.com',
    packages=['biofuzz', 'biofuzz.test'],
    scripts=['bin/bioFuzz'],
    url='http://pypi.python.org/pypi/bioFuzz/',
    license='GPLv3',
    description='bioFuzz',
    long_description=open('README.md').read(),
    install_requires=[],
)

