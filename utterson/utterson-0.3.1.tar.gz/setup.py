from distutils.core import setup

setup(
  name="utterson",
  version='0.3.1',
  author='Jeremy Canady',
  author_email='jcanady@gmail.com',
  description='Management utility for Jekyll based blogs.',
  long_description=open('README_PyPI.rst').read(),
  license='GPLv2',
  keywords='jekyll',
  url='https://github.com/jrmycanady/Utterson',
  scripts=['bin/utterson'],
  packages=['utterson'],
  package_data = {
    'utterson': [
      'templates/jc_simple_blue/jekyll_root/_posts/_deleted/*.*',
      'templates/jc_simple_blue/jekyll_root/_posts/_drafts/*.*',
      'templates/jc_simple_blue/jekyll_root/_posts/_templates/*.*',
      'templates/jc_simple_blue/jekyll_root/_posts/*.*',
      'templates/jc_simple_blue/jekyll_root/css/*.*',
      'templates/jc_simple_blue/jekyll_root/_layouts/*.*',
      'templates/jc_simple_blue/jekyll_root/_includes/*.*',
      'templates/jc_simple_blue/jekyll_root/*.*',
      #'templates/jc_simple_blue/*.*',
      'templates/*.*',
    ],
  },
)