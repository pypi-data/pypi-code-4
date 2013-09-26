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

# import local packages
from ztfy.jqueryui import jquery_17


from zope.i18nmessageid import MessageFactory
_ = MessageFactory('ztfy.bootstrap')


library = Library('ztfy.bootstrap', 'resources')

ztfy_bootstrap_css = Resource(library, 'css/bootstrap.css',
                              minified='css/bootstrap.min.css')

ztfy_bootstrap_responsive_css = Resource(library, 'css/bootstrap-responsive.css',
                                         minified='css/bootstrap-responsive.min.css',
                                         depends=[ztfy_bootstrap_css])

ztfy_bootstrap = Resource(library, 'js/bootstrap.js',
                          minified='js/bootstrap.min.js',
                          depends=[jquery_17, ztfy_bootstrap_css], bottom=True)

ztfy_bootstrap_responsive = Group(depends=[ztfy_bootstrap, ztfy_bootstrap_responsive_css])
