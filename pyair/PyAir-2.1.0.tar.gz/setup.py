from distutils.core import setup

setup(
    name='PyAir',
    version='2.1.0',
    author='Lionel Roubeyrie',
    author_email='lionel.roubeyrie@gmail.com',
    packages=['pyair','windrose'],
    url='http://pypi.python.org/pypi/PyAir/',
    license='LICENSE.txt',
    description='For working with French air quality data and the Iseo XAIR database',
    long_description=open('README.txt').read(),
    install_requires=[
        "cx_Oracle >= 4.0",
        "pandas >= 0.11.0",
        "numpy >= 0.1.0",
        "scipy >= 0.8.0",
        "matplotlib >= 1.2.0",
        "pyproj >= 1.9.0",
        "simplekml >= 1.2.0",
        "pyshp >= 1.1.7"
    ],
)