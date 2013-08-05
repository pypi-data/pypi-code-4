from setuptools import setup, find_packages
import os
os.system("cd docs && make")
os.system("cp docs/README.rst .")
readme = "See documentation at github.com/tomthorogood/MultiString"
try:
    with open("README.md") as readme_md:
        readme = readme_md.read()
except IOError:
    try:
        with open("README.rst") as readme_rst:
            readme = readme_rst.read()
    except IOError:
        pass
setup(
        name = "ac",
        version = "0.3-alpha",
        description="A python library for writing C/C++ configure files.",
        long_description = readme,    
        author="Tom A. Thorogood",
        author_email="tom@tomthorogood.com",
        license="GPLv3",
        url = "http://www.github.com/tomthorogood/AC.py",
        test_suite = 'test',
        packages = find_packages(exclude=['setup.py']),
        zip_safe = True
)

