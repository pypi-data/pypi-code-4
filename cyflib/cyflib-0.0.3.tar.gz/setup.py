from distutils.core import setup
try:
  long_desc = open("cyflib/readme.txt", "r").read()
except:
  long_desc = "Visita http://pypi.python.org/pypi/cyflib"

setup(
    name='cyflib',
    version='0.0.3',
    author='inobagger',
    author_email='inobagger@gmail.com',
    packages=['cyflib', 'cyflib/ecdsa'],
    url='http://cyfnet.tk/cyflib',
    license='Creative Commons Attribution 3.0 Unported License',
    description='CyfNet Python Library',
    long_description=long_desc
)
