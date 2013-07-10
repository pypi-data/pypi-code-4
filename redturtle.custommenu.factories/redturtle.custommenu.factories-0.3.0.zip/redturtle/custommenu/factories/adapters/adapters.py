# -*- coding: utf-8 -*-

import sys

from zope.interface import implements
from zope.component import ComponentLookupError
from Products.CMFCore.utils import getToolByName
from redturtle.custommenu.factories.interfaces import ICustomFactoryMenuProvider
from redturtle.custommenu.factories import custommenuMessageFactory as mf
from redturtle.custommenu.factories import logger

from Products.PageTemplates import Expressions
from zope.tales.tales import CompilerError

from zope.component import getMultiAdapter

if sys.version_info < (2, 6):
    PLONE4 = False
else:
    PLONE4 = True

class MenuCoreAdapter(object):

    def __init__(self, context):
        self.context = context

    def _formatNewEntry(self, customization, url, icon):
        """Return a menu-like structure with the new additional element"""
        return {'title'       : mf(customization['element-name']),
                'description' : mf(customization['element-descr']),
                'action'      : url,
                'selected'    : False,
                'icon'        : icon,
                'submenu'     : None,
                'extra'       : {'separator': None,
                                 'id': customization['element-id'],
                                 'class': PLONE4 and 'contenttype-%s' % customization['element-id'] or ''},
                }

    def getMenuCustomization(self, data, results):
        raise NotImplementedError("You must provide the getMenuCustomization method")


class PloneSiteFactoryMenuAdapter(MenuCoreAdapter):
    implements(ICustomFactoryMenuProvider)

    def _get_menu_customizations(self):
        context = self.context

        try:
            view = getMultiAdapter((context, context.REQUEST), name=u'customize-factoriesmenu')
        except ComponentLookupError:
            return results

        extras, saved_customizations = view.getSavedCustomizations()
        return saved_customizations

    def _calc_menu_entry(self, customization, data, newIds):
        # condition
        talEngine = Expressions.getEngine()
        condition = customization['condition-tales']
        if condition:
            compiledCondition = talEngine.compile(condition)
            try:
                result = compiledCondition(talEngine.getContext(data))
            except KeyError, inst:
                return
            if not result and customization['element-id']:
                newIds.append(customization['element-id'])
                return

        # URL
        url = talEngine.compile(customization['element-tales'])
        try:
            compiledURL = url(talEngine.getContext(data))
        except KeyError, inst:
            logger.error("customize-factoriesmenu error: can't use the \"%s\" TALES expression" % condition)
            return
        # ICON
        icon = talEngine.compile(customization['icon-tales'])
        try:
            compiledIcon = icon(talEngine.getContext(data))
        except KeyError, inst:
            compiledIcon = None
        
        if compiledURL:
            newElement = self._formatNewEntry(customization, compiledURL, compiledIcon)
            if newElement['extra']['id']:
                newIds.append(newElement['extra']['id'])
            return newElement

    def getMenuCustomization(self, data, results):
        """Get saved menu customization for a context that is the Plone site root
        @data: a dict object used for evaluate TALES expressions
        @results: a menu-like structure, normally obtained calling PloneFactoriesMenu.getMenuItems
        @return: the new menu-like structure, with additional customizations
        """
        newResults = []
        newIds = []
        
        saved_customizations = self._get_menu_customizations()
        
        for c in saved_customizations:
            newElement = self._calc_menu_entry(c, data, newIds)
            if not newElement:
                continue
            if newElement['extra']['id']:
                newIds.append(newElement['extra']['id'])
            newResults.append(newElement)

        # Spit off overriden elements, using id
        results = [x for x in results if x['extra']['id'] not in newIds]
        results.extend(newResults)
        return results

    def getSingleEntryMenuCustomization(self, data, fti):
        """
        Customization for single-entry menu item
        @fti: portal_types configuration
        """
        saved_customizations = self._get_menu_customizations()
        foo = []

        for c in saved_customizations:
            if c['element-id'] == fti.id.lower().replace(' ',''):
                newElement = self._calc_menu_entry(c, data, foo)
                return newElement

class FolderFactoryMenuAdapter(PloneSiteFactoryMenuAdapter):
    implements(ICustomFactoryMenuProvider)

    def getMenuCustomization(self, data, results):
        """Get saved menu customization from folderish content. Is also possible to inherit
        customization from the site root (if both inherit checks are True).
        @data: a dict object used for evaluate TALES expressions
        @results: a menu-like structure, normally obtained calling PloneFactoriesMenu.getMenuItems
        @return: the new menu-like structure, with additional customizations
        """
        context = self.context
        portal = getToolByName(context, 'portal_url').getPortalObject()
        try:
            viewOnPortal = getMultiAdapter((portal, context.REQUEST), name=u'customize-factoriesmenu')
        except ComponentLookupError:
            return results
        view = getMultiAdapter((context, context.REQUEST), name=u'customize-factoriesmenu')
        if viewOnPortal.inherit and view.inherit:
            siteResults = ICustomFactoryMenuProvider(portal).getMenuCustomization(data, results)
            results = PloneSiteFactoryMenuAdapter.getMenuCustomization(self, data, siteResults)
        else:
            results = PloneSiteFactoryMenuAdapter.getMenuCustomization(self, data, results)
        return results
