from distutils.core import setup
setup(name='ScrapyEs',
      version='0.2',
      license='Apache License, Version 2.0',
      description='An extension module to send data to elasticsearch in bulk format.',
      author='Ernesto Miguez',
      author_email='ernesto.miguez@asquera.de',
      url='https://github.com/Asquera/scrapy-elasticsearch-extension',
      keywords="scrapy elastic search",
      py_modules=['scrapyes'],
      platforms = ['Any'],
      install_requires = ['scrapy', 'pyes'],
      classifiers = [ 'Development Status :: 4 - Beta',
                      'Environment :: No Input/Output (Daemon)',
                      'License :: OSI Approved :: BSD License',
                      'Operating System :: OS Independent',
                      'Programming Language :: Python']
)
