from setuptools import setup

setup(
    name='hstore-field-caseinsensitive',
    version='1.0.2',
    description="Support for PostgreSQL's hstore for Django.",
    long_description=open('README.md').read(),
    author='Eric Russell',
    author_email='eric-r@pobox.com',
    url='git@github.com:anantasty/hstore-field.git',
    packages=['hstore_field'],
    include_package_data=True,
    license='BSD',
)
