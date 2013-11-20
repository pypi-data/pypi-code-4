from distutils.core import setup

setup(
    name='PyHCUP',
    version='0.1.1dev',
    packages=['pyhcup'],
    license='',
    long_description=open('README.txt').read(),
    provides=['pyhcup'],
    requires=['pandas(>=0.11.0)','pyodbc(>=3.0.6)'],
)