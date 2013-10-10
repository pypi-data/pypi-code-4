from setuptools import setup, find_packages
import os.path

version = '1.2'

readme = open('README.txt').read()
changes = open('CHANGES.txt').read()
usage = open(os.path.join(
    'src', 'z3c', 'bcrypt', 'USAGE.txt')).read()

long_description = '\n\n'.join([readme, usage, changes, ''])

setup(name='z3c.bcrypt',
      version=version,
      description=(
          "Password manager utility using bcrypt or pbkdf2 encoding. "
          "Useful in combination with zope.password"),
      long_description=long_description,
      classifiers = [
          'Development Status :: 5 - Production/Stable',
          'Environment :: Web Environment',
          'Intended Audience :: Developers',
          'License :: OSI Approved :: Zope Public License',
          'Programming Language :: Python',
          'Natural Language :: English',
          'Operating System :: OS Independent',
          'Topic :: Internet :: WWW/HTTP',
          'Framework :: Zope3'],
      keywords='zope authentication password bcrypy pbkdf2',
      author = "The Health Agency and the Zope Community",
      author_email = "zope3-dev@zope.org",
      url='http://pypi.python.org/pypi/z3c.bcrypt',
      license='ZPL 2.1',
      package_dir={'': 'src'},
      packages=find_packages('src'),
      namespace_packages=['z3c'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'cryptacular',
          'zope.interface',
          'zope.password',
          ],
      extras_require = dict(
        test = [
            'zope.testing',
            ],
        ),
      entry_points={
          'console_scripts': []
          },
      )
