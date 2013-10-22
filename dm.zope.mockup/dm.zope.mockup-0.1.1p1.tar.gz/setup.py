from os.path import abspath, dirname, join
try:
  # try to use setuptools
  from setuptools import setup
  setupArgs = dict(
    include_package_data=True,
    namespace_packages=['dm', 'dm.zope'],
    zip_safe=False,
    test_suite='dm.zope.mockup.tests.testsuite',
    test_requires=['ZODB'],
    )
except ImportError:
  # use distutils
  from distutils import setup
  setupArgs = dict(
    )

cd = abspath(dirname(__file__))
pd = join(cd, 'dm', 'zope', 'mockup')

def pread(filename, base=pd): return open(join(base, filename)).read().rstrip()

setup(name='dm.zope.mockup',
      version=pread('VERSION.txt').split('\n')[0],
      description='A (still small) repository of mockup objects for Zope [2] tests.',
      long_description=pread('README.txt'),
      classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Framework :: Zope2',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Utilities',
        ],
      author='Dieter Maurer',
      author_email='dieter@handshake.de',
      url='http://pypi.python.org/pypi/dm.zope.mockup',
      packages=['dm', 'dm.zope', 'dm.zope.mockup'],
      keywords='test mockup',
      license='BSD',
      **setupArgs
      )
