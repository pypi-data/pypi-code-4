from distutils.core import setup

setup(name='shapeways',
      version='0.1.0',
      description='Shapeways python bindings',
      author='Paul Walker',
      author_email='pwalker@fvml.ca',
      url='https://fvml.ca',
      packages=['shapeways'],
      install_requires=['rauth >= 0.6.2'],
)