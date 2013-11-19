from distutils.core import setup

setup(
    name='SysExtension',
    version='0.1.0',
    author='Andrew Udvare',
    author_email='audvare@gmail.com',
    packages=['sysext'],
    url='https://github.com/Appdynamics/python-sysext',
    license='LICENSE.txt',
    description='Extension for sys module, for POSIX systems only',
    long_description=open('README.rst').read(),
)
