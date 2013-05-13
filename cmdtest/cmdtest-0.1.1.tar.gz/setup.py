from distutils.core import setup

setup(
    name='cmdtest',
    version='0.1.1',
    py_modules = ['cmdtest'],
    license='MIT license',
    description='Simple testing for command line programs.',
    long_description=open('README.rst').read(),
    url='https://github.com/chromy/cmdtest',
    author='Hector Dearman',
    author_email='hector.dearman@gmail.com',
)
