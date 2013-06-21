from setuptools import setup, find_packages


with open('README.rst') as f:
    readme = f.read()

with open('LICENSE') as f:
    license = f.read()

setup(
    name='RESTpy',
    version='0.0.1',
    description='Werkzeug extensions for building RESTful services.',
    long_description=readme,
    author='Kevin Conway',
    author_email='kevinjacobconway@gmail.com',
    url='https://github.com/kevinconway/rest.py',
    license=license,
    packages=find_packages(exclude=('tests', 'docs')),
    package_data = {
        '': ['LICENSE', 'CONTRIBUTING', 'requirements.txt', 'README.rst']
    }
)
