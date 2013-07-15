from setuptools import setup

setup(
    name="Ifbyphone-API-Module",
    version='0.0.3',
    url='https://github.com/Opus1no2/Ifbyphone-API-Module',
    description='A Python client for interacting with Ifbyphone REST API',
    package_dir={'': 'src'},
    packages=['Ifbyphone', 'Ifbyphone.api'],
    
    author='Travis Tillotson',
    author_email='tillotson.travis@gmail.com',
    
    license='MIT',
    install_requires=['requests',],
)