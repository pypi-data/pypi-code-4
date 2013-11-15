from distutils.core import setup, Command

# run our tests
class PyTest(Command):
    user_options = []
    def initialize_options(self):
        pass
    def finalize_options(self):
        pass
    def run(self):
        import sys, subprocess
        errno = subprocess.call([sys.executable, 'header_detail_footer.py'])
        raise SystemExit(errno)


setup(name='header-detail-footer',
      version='1.0',
      url='https://bitbucket.org/ericvsmith/header-detail-footer',
      author='Eric V. Smith',
      author_email='eric@trueblade.com',
      description='Parse input streams with headers and footers.',
      long_description=open('README.txt').read() + '\n' + open('CHANGES.txt').read(),
      classifiers=['Development Status :: 5 - Production/Stable',
                   'Intended Audience :: Developers',
                   'License :: OSI Approved :: Apache Software License',
                   'Topic :: Software Development :: Libraries :: Python Modules',
                   'Programming Language :: Python :: 2',
                   'Programming Language :: Python :: 3',
                   ],
      license='Apache License Version 2.0',
      py_modules=['header_detail_footer'],

      cmdclass = {'test': PyTest},
      )
