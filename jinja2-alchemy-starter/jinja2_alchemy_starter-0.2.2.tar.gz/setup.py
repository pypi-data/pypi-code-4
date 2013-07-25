import os
from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))

requires = [
    'pyramid>=1.4',
    ]

with open(os.path.join(here, 'README.txt')) as f: 
    README = f.read()
with open(os.path.join(here, 'CHANGES.txt')) as f: 
    CHANGES = f.read()

setup(name='jinja2_alchemy_starter',
      version='0.2.2',
      description='Pyramid Scaffold for getting started with SQLAlchemy ORM and Jinja2 Templating Engine',
      long_description=README + '\n\n' +  CHANGES,
      author='Dheeraj Gupta',
      author_email='dheeraj.gupta4@gmail.com',
      url='',
      keywords='pylons pyramid scaffolds',
      packages=find_packages(),
      include_package_data=True,
      zip_safe=False,
      install_requires=requires,
      entry_points = """\
        [pyramid.scaffold]
        jinja2_alchemy_starter=jinja2_alchemy_starter.scaffolds:PyJinAlTemplate
      """
      )
