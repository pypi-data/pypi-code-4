from distutils.core import setup
setup(name='scrapymongocache',
      version='0.1.0',
      license='Apache License, Version 2.0',
      description='A base pipeline and a decorator to allow you to cache item fields in MongoDB collections.',
      author='Dimitrios Kouzis-Loukas',
      author_email='info@scalingexcellence.co.uk',
      url='http://github.com/scalingexcellence/scrapy-mongodb-cache-pipeline',
      keywords="scrapy mongodb pipeline",
      py_modules=['scrapymongocache'],
      platforms = ['Any'],
      install_requires = ['scrapy', 'pymongo'],
      classifiers = [ 'Development Status :: 4 - Beta',
                      'Environment :: No Input/Output (Daemon)',
                      'License :: OSI Approved :: Apache Software License',
                      'Operating System :: OS Independent',
                      'Programming Language :: Python']
)
