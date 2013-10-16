from distutils.core import setup

setup(name='wachtwoord',
      version='0.14',
      author='Guido Kollerie',
      author_email='guido@kollerie.com',
      classifiers=['Development Status :: 3 - Alpha',
                   'Programming Language :: Python :: 3',
                   'Topic :: Security :: Cryptography',
                   'Topic :: Software Development :: Libraries'],
      url='https://bitbucket.org/gkoller/wachtwoord',
      packages=['wachtwoord'],
      license='2-clause BSD',
      description='Python 3 password hashing library',
      long_description=open('README').read())
