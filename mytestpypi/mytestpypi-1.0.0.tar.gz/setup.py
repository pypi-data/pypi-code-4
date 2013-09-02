#coding=utf-8
# setup.py
from distutils.core import setup
setup(
  name = 'mytestpypi',
  version = '1.0.0',
  py_modules = ['mytestpypi'], # 将模块的元数据与setup函数的参数关联
  author = 'wwj718',
  author_email = 'wwj718@headfirstlabs.com',
  url = 'http://www.wwj718.com',
  description = 'mytest to use pypi',
)
