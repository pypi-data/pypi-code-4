from os import walk,sep, path
import sys
import os

BASE="""<configure
    xmlns="http://namespaces.zope.org/zope"
    xmlns:browser="http://namespaces.zope.org/browser">
    %s
</configure>
"""

PAGE="""
    <browser:page
             for="*"
             name="%(name)s"
             template="%(template)s"
             permission="zope2.View"
             />
"""

DENIED=['__init__.py','configure.zcml','__init__.pyc','.svn']
BASE_PATH=__path__[0]

string_=''
for file in os.listdir(BASE_PATH):
    if file not in DENIED:
        dict_={}
        dict_['template']=file
        if file.endswith('.pt'):
            file=file[:-3]
        dict_['name']=file

        string_+=PAGE%dict_
fp=open(BASE_PATH+sep+'configure.zcml','w')
fp.write(BASE%string_)
fp.close()