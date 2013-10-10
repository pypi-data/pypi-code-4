from setuptools import setup, find_packages
setup(name='GPU-BSM',
      version='2.4.0',
      description='A GPU-based Tool to Map Bisulfite-Threated Reads',
      author='Andrea Manconi',
      author_email='andrea.manconi@itb.cnr.it',
      license = 'LICENSE-agpl-3.0.txt',
      py_modules=['GPU-BSM-Aligner', 'GPU-BSM-Builder', 'utilities'],
      url='http://www.interomics.eu/',
      install_requires=["pycuda>= 2013.1.1","cutadapt"], 
      packages = find_packages()
      )
