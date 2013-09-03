import os
from setuptools import setup, find_packages

__version__ = '0.5'
__path__ = os.path.dirname(os.path.abspath(__file__))

if __name__ == '__main__':
    setup(
          name = 'pyprotobuf',
          author = "Nate Skulic",
          author_email = "nate.skulic@gmail.com",
          description = "Python protocol buffers compiler",
          long_description = open(os.path.join(__path__, 'README.rst'), 'r').read(),
          version = __version__,
          packages = find_packages(),
          package_dir = {'pyprotobuf':'pyprotobuf'},
          requires = [],
          url='http://code.google.com/p/pyprotobuf',
          install_requires = [],
          entry_points = '''
          [console_scripts]
          pyprotoc = pyprotobuf.main:_main
          
          [pyprotobuf.generators]
            closure = pyprotobuf.generators.closurelib
            python = pyprotobuf.generators.protorpc
            externs = pyprotobuf.generators.externs
          '''
    )
