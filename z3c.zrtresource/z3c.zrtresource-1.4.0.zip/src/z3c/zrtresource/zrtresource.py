##############################################################################
#
# Copyright (c) 2001, 2002 Zope Foundation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""CSS Resource

$Id$
"""
__docformat__='restructuredtext'
from zope.browserresource.file import File, FileResource
from zope.browserresource.interfaces import IResourceFactory
from zope.browserresource.interfaces import IResourceFactoryFactory
from zope.interface import implements, classProvides
from zope.site.hooks import getSite

from z3c.zrtresource import processor, replace


class ZRTFileResource(FileResource):

    def GET(self):
        data = super(ZRTFileResource, self).GET()
        # Process the file
        p = processor.ZRTProcessor(data, commands={'replace': replace.Replace})
        return p.process(getSite(), self.request)


class ZRTFileResourceFactory(object):
    
    implements(IResourceFactory)
    classProvides(IResourceFactoryFactory)

    def __init__(self, path, checker, name):
        self.__file = File(path, name)
        self.__checker = checker
        self.__name = name

    def __call__(self, request):
        resource = ZRTFileResource(self.__file, request)
        resource.__Security_checker__ = self.__checker
        resource.__name__ = self.__name
        return resource
