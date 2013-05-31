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
"""Meta Configure

$Id$
"""
import zope.schema
import zope.configuration.fields
from zope.component.zcml import handler
from zope.interface import Interface
from zope.publisher.interfaces import browser
from zope.security.checker import CheckerPublic, NamesChecker
from zope.browserresource import metadirectives
from zope.browserresource import metaconfigure as resourcemeta

import z3c.zrtresource


class IZRTResourceDirective(metadirectives.IBasicResourceInformation):
    """Defines a browser ZRT resource"""

    name = zope.schema.TextLine(
        title=u"The name of the resource",
        description=u"""
        This is the name used in resource urls. Resource urls are of
        the form site/@@/resourcename, where site is the url of
        "site", a folder with a site manager.

        We make resource urls site-relative (as opposed to
        content-relative) so as not to defeat caches.""",
        required=True
        )

    file = zope.configuration.fields.Path(
        title=u"File",
        description=u"The file containing the resource data.",
        required=True
        )


def zrtresource(_context, name, file, layer=browser.IDefaultBrowserLayer,
                permission='zope.Public'):

    if permission == 'zope.Public':
        permission = CheckerPublic

    checker = NamesChecker(resourcemeta.allowed_names, permission)

    factory = z3c.zrtresource.ZRTFileResourceFactory(file, checker, name)

    _context.action(
        discriminator = ('resource', name, browser.IBrowserRequest, layer),
        callable = handler,
        args = ('registerAdapter',
                factory, (layer,), Interface, name, _context.info),
        )
