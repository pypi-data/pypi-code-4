from setuptools import setup, find_packages
import os

version = '0.1.1'

setup(name='collective.sphinx.includechangelog',
      version=version,
      description="Include changelog extracted from egg information "
                  " into sphinx documentation.",
      long_description=open("README.txt").read() + "\n" +
      open(os.path.join("docs", "HISTORY.txt")).read(),
      classifiers=[
          "Programming Language :: Python",
          "Programming Language :: Python :: 2.7",
          "Operating System :: OS Independent",
          "Topic :: Documentation",
          "Topic :: Software Development :: Libraries :: Python Modules",
      ],
      keywords='sphinx changelog',
      author='Jean Francois Roche',
      author_email='jfroche@affinitic.be',
      url='http://github.com/collective/collective.sphinx.includechangelog',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['collective', 'collective.sphinx'],
      include_package_data=True,
      zip_safe=False,
      install_requires=['docutils', 'Sphinx', 'zc.recipe.egg'],
      )
