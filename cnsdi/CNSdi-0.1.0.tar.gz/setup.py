from distutils.core import setup

setup(
    name='CNSdi',
    version='0.1.0',
    author='Scott Scoble',
    author_email='sscoble@codesmith.ws',
    packages=['di','di.test'],
    license='LICENSE.txt',
    description='Simple Dependency Injection for python',
    long_description=open('README.txt').read(),
    install_requires=[]
)