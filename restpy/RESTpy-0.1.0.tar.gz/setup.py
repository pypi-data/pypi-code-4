from setuptools import setup, find_packages


__version__ = "0.1.0"

with open('README.rst') as f:
    readme = f.read()

with open('LICENSE') as f:
    license = f.read()

setup(
    name='RESTpy',
    version=__version__,
    description='Werkzeug extensions for building RESTful services.',
    long_description=readme,
    author='Kevin Conway',
    author_email='kevinjacobconway@gmail.com',
    url='https://github.com/kevinconway/rest.py',
    license=license,
    include_package_data=True,
    packages=find_packages(exclude=('tests', 'docs')),
    scripts=['restpy/scripts/restpy']
)
