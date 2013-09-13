from distutils.core import setup

setup(name='VirtualMemProtect',
      version='0.1',
      author='Eugene Ching',
      author_email='eugene@enegue.com',
      license='MIT',
      description='Handles querying and setting of memory protection flags in Windows.',
      long_description=open('README.txt').read(),
      py_modules=['virtualmemprotect'],
      scripts=['bin/vprotect.py']
     )

