#encoding:utf-8

from setuptools import setup

setup(name='pydouban',  
      author='TY',  
      author_email='tianyu0915@gmail.com',  
      version='0.0.4',  
      description='A simple python libary for douban.com that contains some basic functions',  
      keywords ='douban,libary',
      url='http://github.com/tianyu0915/pydouban',  
      packages=['pydouban'],  
      install_requires = ['requests==0.13.1','lxml>=2.3.4'],
      license = open('LICENSE').read(),

)  
