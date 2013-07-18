from setuptools import setup, find_packages

setup(name='cs.navigation',
      version = '0.1',
      description="Simple navigation portlet based on plone's but with additional markup checks",
      long_description=open('README.txt').read(),
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Framework :: Plone",
        "Framework :: Zope2",
        "Framework :: Zope3",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='plone portlets navigation',
      author='CodeSyntax',
      author_email='mlarreategi@codesyntax.com',
      url='http://code.codesyntax.com/private/cs.navigation',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['cs'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          # -*- Extra requirements: -*-
          'plone.app.form',
          'plone.app.portlets',
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
