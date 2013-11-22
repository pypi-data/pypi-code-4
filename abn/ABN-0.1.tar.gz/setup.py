from setuptools import setup

setup(
    name='ABN',
    version='0.1',
    py_modules=['abn'],
    test_suite='tests',
    license='Apache 2.0',
    description='Validate Australian Business Numbers.',
    long_description=open('README').read(),
    url='',
    author='Ben Sturmfels',
    author_email='ben@sturm.com.au',
)
