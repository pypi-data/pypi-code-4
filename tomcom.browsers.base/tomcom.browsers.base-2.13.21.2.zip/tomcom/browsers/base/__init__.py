from zope.interface import implements
from Products.Five import BrowserView as BaseBrowserView
from zope.interface import Interface
import warnings

#Daily helper
from Products.CMFCore.utils import getToolByName
from Products.Archetypes.utils import OrderedDict
from DateTime import DateTime

import logging
logger = logging.getLogger('tomcom.browsers.base')


class BrowserView(BaseBrowserView):

    def get_context(self):

        if hasattr(self.context,'UID'):
            rc=self.context.getAdapter('rc')()
            return rc.lookupObject(self.context.UID())
        else:
            return self.context

    def getContext(self):

        logger.warning('BrowserView -> getContext is deprecated please use get_context')

        return self.get_context()

    def __call__(self):
        """ """
        context=self.context
        pt=context.getAdapter('pt')()
        fti=pt.getTypeInfo(context.portal_type)
        value=fti.defaultView(context)
        return getattr(context,value)()