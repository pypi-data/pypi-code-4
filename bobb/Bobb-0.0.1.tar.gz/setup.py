from distutils.core import setup

setup(name='Bobb',
      version='0.0.1',
      description='A minimal build tool written and configurable in python.',
      author='Naman Bharadwaj',
      author_email='namanbharadwaj@gmail.com',
      url='https://github.com/namanbharadwaj/bobb',
      packages=['bobb'],
      package_dir={'': 'src'},
      scripts=['scripts/bobb'],
     )
