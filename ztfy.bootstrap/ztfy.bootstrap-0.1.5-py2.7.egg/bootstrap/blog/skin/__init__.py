### -*- coding: utf-8 -*- ####################################################
##############################################################################
#
# Copyright (c) 2008-2013 Thierry Florac <tflorac AT ulthar.net>
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

__docformat__ = "restructuredtext"

# import standard packages
from fanstatic import Library, Resource, Group

# import Zope3 interfaces

# import local interfaces

# import Zope3 packages
try:
    from ztfy.blog.browser import ztfy_blog_front
except ImportError:
    ztfy_blog_front = None

from ztfy.bootstrap import ztfy_bootstrap, ztfy_bootstrap_css, ztfy_bootstrap_responsive_css
from ztfy.skin import ztfy_skin_base

# import local packages


library = Library('ztfy.bootstrap.blog', 'resources')

ztfy_bootstrap_blog_css = Resource(library, 'css/ztfy.bootstrap.blog.css',
                                   minified='css/ztfy.bootstrap.blog.min.css',
                                   depends=[ztfy_bootstrap_css])

ztfy_bootstrap_blog_responsive_css = Group(depends=[ztfy_bootstrap_blog_css,
                                                    ztfy_bootstrap_responsive_css])

if ztfy_blog_front:
    ztfy_bootstrap_blog = Group(depends=[ztfy_skin_base,
                                         ztfy_blog_front,
                                         ztfy_bootstrap_blog_css,
                                         ztfy_bootstrap])

    ztfy_bootstrap_blog_responsive = Group(depends=[ztfy_bootstrap_blog,
                                                    ztfy_bootstrap_blog_responsive_css])
