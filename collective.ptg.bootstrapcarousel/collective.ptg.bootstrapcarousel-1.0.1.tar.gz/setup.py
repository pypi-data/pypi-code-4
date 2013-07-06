from setuptools import setup, find_packages
import os

version = '1.0.1'

setup(name='collective.ptg.bootstrapcarousel',
      version=version,
      description="Add Bootstraps Carousel to collective.plonetruegallery",
      long_description=open("README.rst").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      # Get more strings from
      # http://pypi.python.org/pypi?:action=list_classifiers
      classifiers=[
        "Framework :: Plone",
        "Programming Language :: Python",
        ],
      keywords='plone plonetruegallery addon',
      author='Jason Murphy',
      author_email='json.murphy@gmail.com',
      url='https://github.com/jsonmurphy/collective.ptg.boostrapcarousel',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['collective', 'collective.ptg'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'collective.plonetruegallery',
      ],
      entry_points="""
      # -*- Entry points: -*-

      [z3c.autoinclude.plugin]
      target = plone
      """,
      )
