### -*- coding: utf-8 -*- ####################################################
##############################################################################
#
# Copyright (c) 2008-2009 Thierry Florac <tflorac AT ulthar.net>
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


from zope.i18nmessageid import MessageFactory
_ = MessageFactory('ztfy.hplskin')

from fanstatic import Library, Resource
from ztfy.blog.defaultskin import ztfy_blog_defaultskin, \
                                  ztfy_blog_defaultskin_css


library = Library('ztfy.hplskin', 'resources')

ztfy_hplskin_css = Resource(library, 'css/hpl.css', minified='css/hpl.min.css',
                            depends=[ztfy_blog_defaultskin_css])

ztfy_hplskin = Resource(library, 'js/hpl.js', minified='js/hpl.min.js',
                        depends=[ztfy_hplskin_css, ztfy_blog_defaultskin], bottom=True)

resources = ztfy_hplskin
