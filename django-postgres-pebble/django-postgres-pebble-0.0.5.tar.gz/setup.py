from setuptools import setup, find_packages

setup(
    name='django-postgres-pebble',
    version='0.0.5',
    description="First-class Postgres feature support for the Django ORM. (Pebble Branch)",
    author='Scott Walton',
    author_email='scw@talktopebble.co.uk',
    license='Public Domain',
    packages=find_packages(),
    install_requires=[
        'bitstring',
        'Django>=1.3',
    ],
)
