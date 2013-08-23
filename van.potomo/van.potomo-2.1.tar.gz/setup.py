import os
from setuptools import setup, find_packages

long_description = (
    '.. contents::\n\n'
    + open(os.path.join('van', 'potomo', 'README.txt')).read()
    + '\n\n'
    + open(os.path.join('CHANGES.txt')).read()
    )


setup(name="van.potomo",
      version='2.1',
      license='ZPL 2.1',
      url='http://pypi.python.org/pypi/van.potomo',
      author_email='zope-dev@zope.org',
      packages=find_packages(),
      author="Vanguardistas LLC",
      description="PO to MO build time compiler",
      long_description=long_description,
      namespace_packages=["van"],
      install_requires = [
          'setuptools',
          'python-gettext'],
      classifiers=[
          'Intended Audience :: Developers',
          'License :: OSI Approved :: Zope Public License',
          'Framework :: Setuptools Plugin',
          'Programming Language :: Python',
          'Development Status :: 5 - Production/Stable',
          'Operating System :: OS Independent',
          'Topic :: Software Development :: Build Tools',
          'Programming Language :: Python :: 3',
          'Programming Language :: Python :: 2',
          ],

      entry_points = """
      [distutils.commands]
      van_build_i18n = van.potomo:van_build_i18n
      """,
      include_package_data = True,
      zip_safe = True,
      )
