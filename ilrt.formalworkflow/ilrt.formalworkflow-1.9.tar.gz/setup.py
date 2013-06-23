from setuptools import setup, find_packages
import os

version = '1.9'

setup(name='ilrt.formalworkflow',
      version=version,
      description="Formal workflow is designed to prevent editing, deletion or reversion of published content from skipping review",
      long_description=open("README.txt").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read() + "\n" +
                       open(os.path.join("docs", "TODO.txt")).read(),      
      classifiers=[
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Environment :: Web Environment",
        "Framework :: Plone",
        "Framework :: Zope2",
        "Framework :: Zope3",
        "Intended Audience :: Developers",
        "Intended Audience :: Other Audience",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
        "Development Status :: 5 - Production/Stable"
        ],
      keywords='web zope plone workflow',
      author='Internet Development, ILRT, University of Bristol',
      author_email='internet-development@bris.ac.uk',
      url='http://bitbucket.org/edcrewe/ilrt.formalworkflow',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['ilrt'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'plone.app.iterate'
      ],
      extras_require = {
        'test': [
            'Products.PloneTestCase',
            'plone.app.testing',
            ]
      },
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
