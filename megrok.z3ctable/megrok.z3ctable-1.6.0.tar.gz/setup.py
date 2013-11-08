from setuptools import setup, find_packages
import os

version = '1.6.0'
readme = open(os.path.join("src", "megrok", "z3ctable", "README.txt")).read()
history = open(os.path.join("docs", "HISTORY.txt")).read()


install_requires = [
    'grokcore.component',
    'grokcore.layout',
    'grokcore.view >= 1.12',
    'martian',
    'setuptools',
    'z3c.table >= 0.8',
    'zope.component >= 3.9.1',
    'zope.publisher',
    ],


test_requires = [
    'zope.site',
    'zope.browserpage',
    'zope.configuration',
    'zope.container',
    'zope.interface',
    'zope.security',
    'zope.testing',
    'zope.traversing',
    ]


setup(name='megrok.z3ctable',
      version=version,
      description="A table component package for Grok based on z3c.table.",
      long_description= u"%s\n\n%s" % (readme, history),
      classifiers=[
          "Framework :: Zope3",
          "Programming Language :: Python",
          "Programming Language :: Zope",
          "Intended Audience :: Developers",
          "Development Status :: 4 - Beta",
          "Topic :: Software Development :: Libraries :: Python Modules",
          ],
      keywords='grok table zope3',
      author='Souheil Chelfouh',
      author_email='trollfot@gmail.com',
      url='http://pypi.python.org/pypi/megrok.z3ctable',
      license='ZPL',
      package_dir={'':'src'},
      packages=find_packages('src', exclude=['ez_setup']),
      namespace_packages=['megrok'],
      include_package_data=True,
      zip_safe=False,
      install_requires=install_requires,
      extras_require={'test': test_requires},
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
