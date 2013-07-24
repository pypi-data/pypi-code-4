# Fortran extension
from numpy.distutils.core import setup, Extension
setup(
  ext_modules = [Extension( 'miescatter', ['miescatter.for'] )],
  name='miescatter',
  version='1.0.0',
  license = "GPL",
  platforms = ["any"],
  author='Dr. Konstantin Shmirko',
)
