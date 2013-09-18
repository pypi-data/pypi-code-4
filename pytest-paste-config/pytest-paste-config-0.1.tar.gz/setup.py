import os
from setuptools import setup


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


setup(
    name='pytest-paste-config',
    license='MIT',
    description='Allow setting the path to a paste config file',
    long_description=read("README.rst"),
    version='0.1',
    py_modules=['pytest_paste_config'],
    entry_points={'pytest11': ['paste-config = pytest_paste_config']},
    install_requires=['pytest>=2.0'],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Topic :: Software Development :: Testing',
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
    ]
)
