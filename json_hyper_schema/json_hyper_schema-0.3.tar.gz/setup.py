from setuptools import setup

__VERSION__ = "0.3"

setup(
    name='json_hyper_schema',
    version=__VERSION__,
    packages=['json_hyper_schema'],
    long_description=open('./README.rst').read(),
    author='Ernst Odolphi',
    author_email='ernst.odolphi@gmail.com',
    install_requires=['iso8601', 'requests', 'json-patch', 'json-pointer',
                      'json-reference', 'ipaddress', 'validate_email']
)



