from setuptools import setup, find_packages
import os

version = '1.0a1'

setup(name='c2.patch.z3cformdateinput',
      version=version,
      description="This product is monkey patch for z3cform date input box for Japanese style",
      long_description=open("README.txt").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      # Get more strings from
      # http://pypi.python.org/pypi?:action=list_classifiers
      classifiers=[
        "Framework :: Plone",
        "Programming Language :: Python",
        ],
      keywords='plone patch dateinput dexterity',
      author='Manabu TERADA',
      author_email='terada@cmscom.jp',
      url='http://wwww.cmscom.jp',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['c2', 'c2.patch'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          # -*- Extra requirements: -*-
          'collective.z3cform.datetimewidget',
      ],
      entry_points="""
      # -*- Entry points: -*-

      [z3c.autoinclude.plugin]
      target = plone
      """,
      )
