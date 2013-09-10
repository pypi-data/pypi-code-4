import os
from setuptools import setup, find_packages

setup(
    install_requires = [
        'SQLAlchemy>=0.7,<=0.7.99',
        'pyodbc>=3.0.7',
    ],
    name='vertica-sqlalchemy-0.2',
    version='0.2',
    description='Vertica dialect for sqlalchemy',
    long_description=open("PKG-INFO").read(),
    author='Shivam Shukla',
    author_email='shivam.shukla@globallogic.com',
    license="MIT",
    url='https://bitbucket.com/shivamshukla/vertica-sqlalchemy-hpcs',
    packages=find_packages(exclude=["tests.*", "tests"]),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
    ],
    entry_points="""
    [sqlalchemy.dialects]
    vertica.pyodbc = verticasa.verticasa:Vertica
    """
)

