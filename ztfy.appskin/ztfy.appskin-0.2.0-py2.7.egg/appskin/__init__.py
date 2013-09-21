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
from fanstatic import Library, Resource

# import Zope3 interfaces

# import local interfaces

# import Zope3 packages

# import local packages
from ztfy.bootstrap import ztfy_bootstrap_responsive, ztfy_bootstrap_responsive_css
from ztfy.skin import ztfy_skin_base


from zope.i18nmessageid import MessageFactory
_ = MessageFactory('ztfy.appskin')


library = Library('ztfy.appskin', 'resources')

ztfy_appskin_css = Resource(library, 'css/ztfy.appskin.css',
                            minified='css/ztfy.appskin.min.css',
                            depends=[ztfy_bootstrap_responsive_css])
ztfy_appskin_grey_css = Resource(library, 'css/ztfy.appskin.grey.css',
                                 minified='css/ztfy.appskin.grey.min.css',
                                 depends=[ztfy_appskin_css])

ztfy_appskin = Resource(library, 'js/ztfy.appskin.js',
                        minified='js/ztfy.appskin.min.js',
                        depends=[ztfy_bootstrap_responsive, ztfy_skin_base, ztfy_appskin_grey_css],
                        bottom=True)
