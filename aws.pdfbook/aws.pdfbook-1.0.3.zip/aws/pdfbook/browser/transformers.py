# -*- coding: utf-8 -*-
# $Id: transformers.py 116190 2010-04-26 20:36:44Z glenfant $
"""Transformers for standard types"""

from zope.component import getMultiAdapter, queryMultiAdapter
from Acquisition import aq_inner
from Products.Five.browser import BrowserView
from Products.CMFDynamicViewFTI.interface import ISelectableBrowserDefault
from aws.pdfbook import logger


class DefaultLayout(BrowserView):
    """Default view for most ATContentType contents
    assuming the content body is in macro "main"
    """

    def contentBody(self):
        context = aq_inner(self.context)
        if ISelectableBrowserDefault.providedBy(context):
            layout = context.getLayout()
        else:
            portal_types = getMultiAdapter((context, self.request),
                                           name=u'plone_tools').types()
            type_info = portal_types.getTypeInfo(context)
            try:
                view_action = type_info.getActionInfo('object/view')
                layout = (view_action['url'].split('/')[-1] or
                          getattr(type_info, 'default_view', 'view'))
            except:
                logger.error("No layout available for %s", context.absolute_url())
                # We can't have a layout
                return False
        return context.restrictedTraverse(layout).macros.get('main', False)


class AbstractFolderishLayout(BrowserView):
    """Layout for any folderish content
    (abstract class must be subclassed)
    """
    def viewItems(self):
        out = []
        items = self._collectItems()
        for item in items:
            enabled = queryMultiAdapter((item, self.request), name=u'aws.pdfbook.enabled')
            if not enabled():
                continue
            out.append(item)
        return out

    def _collectItems(self):
        """Subclasses must override this method
        """
        raise NotImplementedError("Your subclass must provide a '_collectItems' method")


class FolderLayout(AbstractFolderishLayout):
    """For any folder or subclass
    """
    def _collectItems(self):
        context = aq_inner(self.context)
        return context.folderlistingFolderContents(suppressHiddenFiles=True)


class TopicLayout(AbstractFolderishLayout):
    """For any Colletcion/Topic and subclasses
    """
    def _collectItems(self):
        context = aq_inner(self.context)
        return context.queryCatalog(full_objects=True)
