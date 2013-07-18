import os
from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))

requires = [
    'pyramid>=1.4',
    'SQLAlchemy',
    'pyramid_jinja2',
    'jinja2',
    ]

README = open(os.path.join(here, 'README.txt')).read()
CHANGES = open(os.path.join(here, 'CHANGES.txt')).read()

setup(name='jinja2_alchemy_starter',
      version='0.2.1',
      description='Pyramid Scaffold for getting strted with SQLAlchemy ORM and Jinja2 Templating Engine',
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
