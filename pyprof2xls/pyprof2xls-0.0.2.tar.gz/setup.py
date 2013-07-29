from setuptools import setup, find_packages
from pyprof2xls.commands import PYPROF2XLS_VERSION

setup(
        author='Ana Nelson',
        author_email='ana@ananelson.com',
        classifiers=[
            "Environment :: Console",
            "License :: OSI Approved :: MIT License",
            ],
        description='',
        entry_points = {
            'console_scripts' : [
                'pyprof2xls = pyprof2xls.commands:run'
                ]
            },
        include_package_data = True,
        install_requires = [
            'xlwt',
            'python-modargs',
            ],
        name='pyprof2xls',
        packages=find_packages(),
        url='http://github.com/ananelson/pyprof2xls',
        version=PYPROF2XLS_VERSION
        )
