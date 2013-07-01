from setuptools import setup

setup(
    name="Ifbyphone-API-Module",
    version='0.0.1',
    url='https://github.com/Opus1no2/Ifbyphone-API-Module',
    description='A Python client for interacting with Ifbyphone REST API',
    package_dir={'': 'src'},
    packages=['Ifbyphone'],
    
    author='Travis Tillotson',
    author_email='tillotson.travis@gmail.com',
    
    install_requires=['request',],
)