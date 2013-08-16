# -*- coding:utf-8 -*-
import sys
sys.path.append('./webot')
from distutils.core import setup
from webot import __version__

setup(name='webot',
      version=__version__,
      description='A simple weixin bot',
      long_description=open("README.md").read(),
      author='solos',
      author_email='lxl1217@gmail.com',
      packages=['webot'],
      package_dir={'webot': 'webot'},
      package_data={'webot': ['stuff']},
      license="MIT",
      platforms=["any"],
      url='https://github.com/solos/webot')
