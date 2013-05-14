from setuptools import setup, find_packages
import os

version = '1.1rc6'

setup(name='ityou.whoisonline',
      version=version,
      description="Plone Product - Show users who are online",
      long_description=open("README.txt").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      classifiers=[
        "Framework :: Plone",
        "Programming Language :: Python",
        ],
      keywords='Plone Who Online',
      author='ITYOU/LM',
      author_email='lm@ityou.de',
      url='http://www.ityou.de/esi/ityou.whoisonline',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['ityou'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          # -*- Extra requirements: -*-
          'plone.app.portlets',
          'pysqlite',
          'sqlalchemy'
      ],
      entry_points="""
      # -*- Entry points: -*-

      [z3c.autoinclude.plugin]
      target = plone
      """,
      setup_requires=["PasteScript"],
      paster_plugins=["ZopeSkel"],
      )
