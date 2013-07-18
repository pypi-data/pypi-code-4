from setuptools import setup, find_packages
import os

version = '1.3'

setup(name='cs.plt.contentnegotiator',
      version=version,
      description="A patch to get PloneLanguageTool's contentnegotiator work in virtual hosting environment",
      long_description=open("README.txt").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Framework :: Plone",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='',
      author='Plone Foundation',
      author_email='plone-developers@lists.sourceforge.net',
      url='http://svn.plone.org/svn/plone/plone.app.example',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['cs', 'cs.plt'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          # -*- Extra requirements: -*-
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
