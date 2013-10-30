#Pure Python distribution (by packages)
from distutils.core import setup
setup(name='wlab',
      version='1.1.5',
      description='wlab::Wu Xuping\'s Python Distribution Utilities',
      long_description=open('README.txt').read(),           
      author='Wu Xuping',
      author_email='wuxuping@ahjzu.edu.cn',
      url='http://pypi.python.org/pypi/wlab/',
      license='LICENSE.txt',
      package_dir={'wlab': 'src'},
      packages=['wlab'],   
      )
