#############################################################################
#
# Copyright (c) 2010 Zope Foundation and Contributors.
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
import martian
import grok


class SecurityError(grok.GrokError):
    pass


_require_marker = object()


class CheckRequireGrokker(martian.ClassGrokker):
    """Ensure every grok.View has a grok.require directive"""
    martian.component(grok.View)
    martian.directive(grok.require, default=_require_marker)

    def execute(self, factory, config, require, **kw):
        if require is _require_marker:
            raise SecurityError(
                'megrok.strictrequire requires %r to use the grok.require '
                'directive!' % factory, factory)
        return True


class CheckRequireGrokkerPage(CheckRequireGrokker):
    """Ensure every grok.Page has a grok.require directive"""
    martian.component(grok.Page)


class CheckRequireGrokkerViewlet(CheckRequireGrokker):
    """Ensure every grok.Viewlet has a grok.require directive"""
    martian.component(grok.Viewlet)


class CheckRequireGrokkerForm(CheckRequireGrokker):
    """Ensure every grok.Form has a grok.require directive"""
    martian.component(grok.Form)


class CheckRequireGrokkerAddForm(CheckRequireGrokker):
    """Ensure every grok.AddForm has a grok.require directive"""
    martian.component(grok.AddForm)


class CheckRequireGrokkerEditForm(CheckRequireGrokker):
    """Ensure every grok.EditForm has a grok.require directive"""
    martian.component(grok.EditForm)


class CheckRequireRESTGrokker(martian.MethodGrokker):
    """Ensure every grok.REST has a grok.require directive"""
    martian.component(grok.REST)
    martian.directive(grok.require, default=_require_marker)

    def execute(self, factory, method, config, require, **kw):
        if require is _require_marker:
            raise SecurityError(
                'megrok.strictrequire requires %r to use the grok.require '
                'directive on the method: %s!' % (factory, method), factory)
        return True


class CheckRequireXMLPRCGrokker(CheckRequireRESTGrokker):
    martian.component(grok.XMLRPC)


class CheckRequireJSONGrokker(CheckRequireRESTGrokker):
    martian.component(grok.JSON)
