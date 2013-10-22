from setuptools import setup

__VERSION__ = '0.1.0'

setup(
    name='json_reference',
    version=__VERSION__,
    url="https://bitbucket.org/eodolphi/json-reference/",
    py_modules=['json_reference'],
    description='Simple implementation of the json-reference spec',
    long_description=open('./README.rst').read(),
    author='Ernst Odolphi',
    author_email='ernst.odolphi@gmail.com',
    install_requires=['json-pointer', 'requests'],
    tests_require=['mock', 'nose'],
    test_suite='nose.collector'
)



