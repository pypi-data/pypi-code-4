from distutils.core import setup
import glob

setup(name='offtrac',
      version='0.1.0',
      description='Trac xmlrpc library',
      author='Jesse Keating',
      author_email='jkeating@redhat.com',
      url='http://fedorahosted.org/offtrac',
      license='GPLv2+',
      classifiers=[
          'Programming Language :: Python :: 2',
          'Programming Language :: Python :: 3',
      ],
      package_dir = {'': 'src'},
      packages = ['offtrac'],
      )
