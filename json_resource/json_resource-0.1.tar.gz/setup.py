from setuptools import setup

__VERSION__ = '0.1'

setup(
    name='json_resource',
    version=__VERSION__,
    packages=['json_resource'],
    license='Copyright Sanoma Media',
    long_description=open('./README.rst').read(),
    author='Ernst Odolphi',
    author_email='ernst.odolphi@gmail.com',
    install_requires=['json_pointer', 'json_hyper_schema', 'json_patch', 'requests',
                      'pymongo'],
    tests_require=['mock', 'nose'],
    test_suite='nose.collector'
)




