from distutils.core import setup
setup(name='GPU-BSM',
      version='2.3.4',
      description='A GPU-based Tool to Map Bisulfite-Threated Reads',
      author='Andrea Manconi',
      author_email='andrea.manconi@itb.cnr.it',
      license = 'LICENSE-agpl-3.0.txt',
      py_modules=['GPU-BSM-Aligner', 'GPU-BSM-Builder', 'utility'],
      data_files=[('', ['LICENSE-agpl-3.0.txt']), ('', ['Manual.pdf'])],
      url='http://pypi.python.org/pypi/GPU-BSM/',
      install_requires=[
        "pycuda >= 2013.1.1",
      ],
      )
