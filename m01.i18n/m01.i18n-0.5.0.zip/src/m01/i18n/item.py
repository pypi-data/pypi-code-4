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
$Id: item.py 3738 2013-06-08 05:03:57Z roger.ineichen $
"""
__docformat__ = 'restructuredtext'

import datetime

import bson.objectid

import zope.interface
import zope.component
import zope.location.interfaces
import zope.security.management
import zope.i18n.interfaces

import m01.mongo.interfaces
import m01.mongo.base
from m01.mongo import UTC
from m01.mongo.fieldproperty import MongoFieldProperty

from m01.i18n import interfaces

_marker = object()


def getRequest():
    try:
        interaction = zope.security.management.getInteraction()
        request = interaction.participations[0]
    except zope.security.interfaces.NoInteraction:
        request = None
    except IndexError:
        request = None
    return request


class I18nMongoSubItem(m01.mongo.base.SetupConvertDump):
    """I18n sub item"""

    zope.interface.implements(interfaces.II18nMongoSubItem)

    __name__ = None
    _type = None
    _m_changed_value = None

    # built in skip and dump names
    _skipNames = []
    _dumpNames = ['__name__', '_type', 'created', 'modified']

    # customize this in your implementation
    skipNames = []
    dumpNames = []

    created = MongoFieldProperty(interfaces.II18nMongoSubItem['created'])
    modified = MongoFieldProperty(interfaces.II18nMongoSubItem['modified'])

    def __init__(self, data):
        """Initialize a I18nMongoSubItem with given data."""
        # set given language as __name__
        __name__ = data.pop('__name__', _marker)
        if __name__ is not _marker:
            self.__dict__['__name__'] = __name__

        # set given or None __parent__
        __parent__ = data.pop('__parent__', None)
        if __parent__ is not None:
            self.__parent__ = __parent__

        # set given or new _type
        _type = data.pop('_type', self.__class__.__name__)
        if _type != self.__class__.__name__:
            raise TypeError("Wrong mongo item _type used")
        self.__dict__['_type'] = unicode(_type)

        # set given or new created datetime
        created = data.pop('created', _marker)
        if created is _marker:
            created = datetime.datetime.now(UTC)
        self.__dict__['created'] = created

        # update object with given key/value data
        self.setup(data)

        # it is very important to set _m_changed_value to None, otherwise each
        # read access will end in a write access.
        self._m_changed_value = None

    @apply
    def _m_changed():
        def fget(self):
            return self._m_changed_value
        def fset(self, value):
            if value == True:
                self._m_changed_value = value
                if self.__parent__ is not None:
                    self.__parent__._m_changed = value
            elif value != True:
                raise ValueError("Can only dispatch True to __parent__")
        return property(fget, fset)

    def dump(self, dumpNames=None, dictify=False):
        if self._m_changed and (dumpNames is None or 'modified' in dumpNames):
            self.modified = datetime.datetime.now(UTC)
        return super(I18nMongoSubItem, self).dump(dumpNames)


class I18nMongoItemBase(m01.mongo.base.MongoItemBase):
    """II18n mongo item base class"""

    zope.interface.implements(interfaces.II18nItem)

    # default language
    _lang = MongoFieldProperty(interfaces.II18nItem['lang'])
    i18n = MongoFieldProperty(interfaces.II18nItem['i18n'])
    
    # built in skip and dump names
    _dumpNames = ['_id', '_pid', '_type', '_version', '__name__',
                  'created', 'modified',
                  'i18n', 'lang']

    # Subclass MUST implement own converter and use the relevant class for i18n
    converters = {'i18n': I18nMongoSubItem}

    # II18nRead
    @apply
    def lang():
        def fget(self):
            return self._lang
        def fset(self, lang):
            if not lang:
                raise ValueError("Can't set an empty value as language", lang)
            if self._m_initialized and lang not in self.i18n:
                raise ValueError(
                    'cannot set non existent lang (%s) as default' % lang)
            self._lang = unicode(lang)
        return property(fget, fset)

    def getAvailableLanguages(self):
        keys = self.i18n.keys()
        keys.sort()
        return keys

    def getPreferedLanguage(self):
        # evaluate the negotiator
        lang = None
        request = getRequest()
        negotiator = None
        try:
            negotiator = zope.component.queryUtility(
                zope.i18n.interfaces.INegotiator, name='', context=self)
        except zope.component.ComponentLookupError:
            # can happens during tests without a site and sitemanager
            pass
        if request and negotiator:
            lang = negotiator.getLanguage(self.getAvailableLanguages(), request)
        if lang is None:
            lang = self.lang
        if lang is None:
            # fallback lang for functional tests, there we have a cookie request
            lang = 'en'
        return lang

    def getAttribute(self, name, lang=None):
        # preconditions
        if lang is None:
            lang = self.lang

        if not lang in self.getAvailableLanguages():
            raise KeyError(lang)

        # essentials
        data = self.i18n[lang]
        return getattr(data, name)
        
    def queryAttribute(self, name, lang=None, default=None):
        try:
            return self.getAttribute(name, lang)
        except (KeyError, AttributeError):
            return default

    # II18nRead
    def addLanguage(self, lang, obj):
        if not (obj.__name__ is None or obj.__name__ == lang):
            raise TypeError("Obj must provide the lang as __name__ or None")
        obj.__name__ = lang
        self.i18n.append(obj)

    def removeLanguage(self, lang):
        if lang == self.lang:
            raise ValueError('cannot remove default lang (%s)' % lang)
        elif lang not in self.i18n:
            raise ValueError('cannot remove non existent lang (%s)' 
                % lang)
        else:
            del self.i18n[lang]
            self._m_changed = True

    def setAttributes(self, lang, **kws):
        # preconditions
        if not lang in self.getAvailableLanguages():
            raise KeyError(lang)

        obj = self.i18n[lang]
        
        for key in kws:
            if not hasattr(obj, key):
                raise KeyError(key)

        # essentials
        for key in kws:
            setattr(obj, key, kws[key])
        else:
            self._m_changed = True


class I18nMongoContainerItem(I18nMongoItemBase):
    """Simple mongo container item.
    
    Implement your own II18nMongoContainerItem with the attributes you need.
    """

    zope.interface.implements(interfaces.II18nMongoContainerItem,
         m01.mongo.interfaces.IMongoParentAware,
         zope.location.interfaces.ILocation)

    # validate __name__ and observe to set _m_changed
    __name__ = MongoFieldProperty(zope.location.interfaces.ILocation['__name__'])


class I18nMongoStorageItem(I18nMongoItemBase):
    """Simple mongo storage item.
    
    This MongoItem will use the mongo ObjectId as the __name__. This means
    you can't set an own __name__ value for this object.

    Implement your own II18nMongoStorageItem with the attributes you need.
    """

    zope.interface.implements(interfaces.II18nMongoStorageItem,
        m01.mongo.interfaces.IMongoParentAware,
        zope.location.interfaces.ILocation)

    _skipNames = ['__name__']

    @property
    def __name__(self):
        return unicode(self._id)
