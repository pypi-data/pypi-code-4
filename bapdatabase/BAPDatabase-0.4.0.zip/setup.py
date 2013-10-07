from setuptools import setup, find_packages

setup(name='BAPDatabase',
    version='0.4.0',
    author='Eau de Web',
    author_email='office@eaudeweb.ro',
    url='http://naaya.eaudeweb.ro',
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    install_requires=['MySQL-python',
        'z3c.sqlalchemy']
)
