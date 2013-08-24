from distutils.core import setup

with open('README.txt') as readme:
    long_description = readme.read()

setup(name="PyContractor",
    version="0.1.1",
    description="Design By Contract library",
    long_description=long_description,
    author="Ernesto Bossi",
    author_email="bossi.ernestog@gmail.com",
    url="https://github.com/bossiernesto/PyContractor",
    license="GPL v3",
    packages=['PyContractor'],
    package_dir={'PyContractor': 'PyContractor'},
    keywords="Design Contract ContractProgramming",
    classifiers=["Development Status :: 3 - Alpha",
                 "Topic :: Utilities",
                 "License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)"]
)