from distutils.core import setup
setup(
    name='cyflib',
    version='0.0.2',
    author='inobagger',
    author_email='inobagger@gmail.com',
    packages=['cyflib', 'cyflib/ecdsa'],
    url='http://cyfnet.tk/cyflib',
    license='Creative Commons Attribution 3.0 Unported License',
    description='CyfNet Python Library',
    long_description=open('cyflib/readme.txt', 'r').read()
)
