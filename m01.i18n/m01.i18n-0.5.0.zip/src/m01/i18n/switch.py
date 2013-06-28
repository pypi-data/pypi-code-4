##############################################################################
#
# Copyright (c) 2013 Zope Foundation and Contributors.
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
"""
$Id: switch.py 3740 2013-06-11 04:54:07Z roger.ineichen $
"""
__docformat__ = 'restructuredtext'

import zope.interface

from m01.i18n import interfaces


class I18nSwitch(object):
    """Mixing class for switch a language on a object"""
    zope.interface.implements(interfaces.II18nSwitch)

    _lang = 'en'

    def __init__(self, context):
        self.context = context
        self.i18n = self.context
        self._lang = self.i18n.lang

    # II18nSwitch interface
    @apply
    def lang():
        def fget(self):
            return self._lang
        def fset(self, lang):
            if not lang:
                raise ValueError("Can't set an empty value as language", lang)
            self._lang = lang
        return property(fget, fset)


class I18nAdapter(object):
    """Mixing class for i18n adapters which must provide the adapted object 
       under the attribute 'self.i18n'.
    """
    zope.interface.implements(interfaces.II18nAware)

    # II18nRead
    @apply
    def lang():
        def fget(self):
            return self.i18n.lang
        def fset(self, lang):
            self.i18n.lang = lang
        return property(fget, fset)

    # II18nRead
    def getAvailableLanguages(self):
        return self.i18n.getAvailableLanguages()

    def getPreferedLanguage(self):
        return self.i18n.getPreferedLanguage()

    def getAttribute(self, name, lang=None):
        return self.i18n.getAttribute(name, lang)
        
    def queryAttribute(self, name, lang=None, default=None):
        return self.i18n.queryAttribute(name, lang, default)

    # II18nWrite
    def addLanguage(self, lang, obj):
        return self.i18n.addLanguage(lang, obj)

    def removeLanguage(self, lang):
        self.i18n.removeLanguage(lang)

    def setAttributes(self, lang, **kws):
        self.i18n.setAttributes(lang, **kws)
