from distutils.core import setup
setup(name='kat',
      version='0.1.10',
      description='An unofficial Python API for http://kickass.to/',
      url='https://github.com/stephan-mclean/KAT',
      author='Stephan McLean',
      author_email='stephan.mclean2@mail.dcu.ie',
      license='MIT',
      py_modules=['kat'],
      install_requires=['beautifulsoup4>=4.3.2', 'requests>=1.1.0'])