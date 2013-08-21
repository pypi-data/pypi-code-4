from setuptools import setup, find_packages

setup(
    name='pyquchk',
    version='0.1',
    packages=find_packages(),
    url='',
    license='',
    author='Alexander Plavin',
    author_email='alexander@plav.in',
    description='Easy-to-use, extensible random testing (insired by QuickCheck) library.',
    test_requires=['nose'],
    install_requires=['six', 'decorator']
)
