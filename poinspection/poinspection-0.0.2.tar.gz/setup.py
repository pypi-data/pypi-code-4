from setuptools import setup, find_packages

version = '0.0.2'

setup(
    name='poinspection',
    version=version,
    description='Python inspection magic functions for ipython',
    long_description=open('README.md').read(),
    classifiers=[
        "Programming Language :: Python",
        "Intended Audience :: Developers",
        "License :: CC0 1.0 Universal (CC0 1.0) Public Domain Dedication",
        "Operating System :: OS Independent",
    ],
    keywords='ipython',
    author='Luis Montiel',
    author_email='luismmontielg@gmail.com',
    url='https://github.com/luismmontielg/poinspection',
    license='Creative Commons CC0 1.0 Universal (CC0 1.0) Public Domain Dedication',
    packages=find_packages(),
    include_package_data=True,
    zip_safe=True,
    install_requires=[
        'ipython',
    ]
)
