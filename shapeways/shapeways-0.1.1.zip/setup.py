from distutils.core import setup

setup(name='shapeways',
      version='0.1.1',
      description='Shapeways python bindings',
      author='Paul Walker',
      author_email='pwalker@fvml.ca',
      url='https://github.com/pauldw/shapeways-python',
      packages=['shapeways'],
      install_requires=['rauth >= 0.6.2'],
)