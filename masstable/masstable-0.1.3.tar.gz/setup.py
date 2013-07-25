from setuptools import setup, find_packages

setup(
    name='masstable',
    version='0.1.3',
    author='Yaser Martinez',
    author_email='yaser.martinez@gmail.com',
    packages=find_packages(),
    include_package_data=True,
    zip_safe = False,
    package_data={'masstable': ['masstable/data/*.txt']},
    url='https://github.com/elyase/masstable',
    license='MIT',
    description='Utilities for working with nuclear mass tables.',
    long_description=open('README.txt').read(),
    install_requires=[
        "pandas >= 0.11.0"
    ],
)