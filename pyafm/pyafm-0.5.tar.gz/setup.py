"pyafm: tools for controlling atomic force microscopes."

classifiers = """\
Development Status :: 2 - Pre-Alpha
Intended Audience :: Developers
Intended Audience :: Science/Research
Operating System :: POSIX
Operating System :: Unix
License :: OSI Approved :: GNU General Public License (GPL)
Programming Language :: Python
Topic :: Scientific/Engineering
Topic :: Software Development :: Libraries :: Python Modules
"""

from distutils.core import setup
from os import walk
import os.path

from pyafm import __version__


package_name = 'pyafm'


setup(name=package_name,
      version=__version__,
      maintainer='W. Trevor King',
      maintainer_email='wking@tremily.us',
      url='http://blog.tremily.us/posts/{}/'.format(package_name),
      download_url='http://git.tremily.us/?p={}.git;a=snapshot;h=v{};sf=tgz'.format(
        package_name, __version__),
      license='GNU General Public License (GPL)',
      platforms=['all'],
      description=__doc__,
      long_description=open('README', 'r').read(),
      classifiers=filter(None, classifiers.split('\n')),
      packages=['pyafm'],
      provides=['pyafm (%s)' % __version__],
      requires=[
        'pypiezo (>= 0.6)', 'stepper (>= 0.3)', 'h5config (>= 0.2)', 'scipy'],
      )
