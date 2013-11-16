from setuptools import setup, find_packages

version = '1.0'

setup(name='jirathumper',
      version=version,
      description="Parse JimFlowKlopfer JSON output files and update JIRA. Replaces the PHP cron job in JimFlowWall.",
      long_description=open('README.rst').read(),
      classifiers=[], # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      keywords='jimflow kanban jira',
      author='Martin Aspeli',
      author_email='optilude@gmail.com',
      url='',
      license='GPL',
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'requests==2.0.0'
      ],
      entry_points="""
      [console_scripts]
      jirathumper = jirathumper.main:run
      """,
      )
