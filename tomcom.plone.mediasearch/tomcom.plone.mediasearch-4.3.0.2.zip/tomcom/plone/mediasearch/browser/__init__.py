from os import walk,sep, path
import sys
import os

BASE="""<configure
    xmlns="http://namespaces.zope.org/zope"
    xmlns:browser="http://namespaces.zope.org/browser">
    %s
</configure>
"""

PACKAGE="""
    <include package=".%(name)s" />
"""

BASE_PATH=__path__[0]

string_=''
for file in os.listdir(BASE_PATH):
    if len(file.split('.'))==1:
        dict_={}
        dict_['name']=file

        string_+=PACKAGE%dict_
fp=open(BASE_PATH+sep+'configure.zcml','w')
fp.write(BASE%string_)
fp.close()