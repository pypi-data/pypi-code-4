from setuptools import setup, find_packages
import os

version = '0.10.3'

def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

long_description = (
    read('README.txt')
    + '\n' +
    read('js', 'icanhaz', 'test_icanhaz.js.txt')
    + '\n' +
    read('CHANGES.txt'))

setup(
    name='js.icanhaz',
    version=version,
    description="Fanstatic packaging of ICanHaz.js",
    long_description=long_description,
    classifiers=[],
    keywords='',
    url='https://github.com/dnozay/js.ICanHaz',
    author='Damien Nozay',
    author_email='damien.nozay@gmail.com',
    license='BSD',
    packages=find_packages(),namespace_packages=['js'],
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'fanstatic',
        'setuptools',
        ],
    entry_points={
        'fanstatic.libraries': [
            'icanhaz.js = js.icanhaz:library',
            ],
        },
    )
