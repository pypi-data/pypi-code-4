from setuptools import setup, find_packages

setup(name='FTTools',
      version='1.1.6',
      
      description='SkyTruth Fusion Table Tools',
      author='Paul Woods',
      author_email='pau@skytruth.org',
      url='http://www.skytruth.org/',
      packages=find_packages(),
      scripts=['scripts/ft-sync']      
      )
      
#setup(name='FTTools',
#      version='1.1.5',
#      
#      description='SkyTruth Fusion Table Tools',
#      author='Paul Woods',
#      author_email='pau@skytruth.org',
#      url='http://www.skytruth.org/',
#      packages=find_packages(),
#      scripts=['scripts/ft-sync']      
#      )      
