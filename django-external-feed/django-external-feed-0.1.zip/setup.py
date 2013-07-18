from setuptools import setup, find_packages

version = '0.1'

setup(name='django-external-feed',
      version=version,
      description="Show content from an XML feed on your own site.",
      long_description=open('README.rst').read() + '\n\n'+ open('CHANGES.rst').read(),
      # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      classifiers=['Development Status :: 3 - Alpha',
                   'Environment :: Web Environment',
                   'Framework :: Django',
                   'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
                   'Operating System :: OS Independent',
                   'Programming Language :: Python',
                   ],
      keywords='rss atom syndication',
      author='Maurits van Rees',
      author_email='m.van.rees@zestsoftware.nl',
      url='https://github.com/nederhoed/django-external-feed',
      license='GPL',
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'feedparser',
      ],
      )
