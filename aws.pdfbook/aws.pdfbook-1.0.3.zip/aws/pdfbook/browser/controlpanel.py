# -*- coding: utf-8 -*-
# $Id: controlpanel.py 116190 2010-04-26 20:36:44Z glenfant $
"""Control panel"""

from zope.interface import implements
from zope.component import adapts
from zope.formlib import form
from plone.app.controlpanel.form import ControlPanelForm
from Products.CMFCore.utils import getToolByName
from Products.CMFDefault.formlib.schema import SchemaAdapterBase
from Products.CMFDefault.formlib.schema import ProxyFieldProperty
from Products.CMFPlone.interfaces import IPloneSiteRoot
from Products.CMFPlone.utils import getSiteEncoding

from aws.pdfbook.interfaces import IPDFOptions
from aws.pdfbook.config import PROPERTYSHEET
from aws.pdfbook import translate as _


class PDFOptions(SchemaAdapterBase):

    implements(IPDFOptions)
    adapts(IPloneSiteRoot)

    def __init__(self, context):
        super(PDFOptions, self).__init__(context)
        self.portal = context
        pprop = getToolByName(self.portal, 'portal_properties')
        self.context = getattr(pprop, PROPERTYSHEET)
        self.encoding = getSiteEncoding(context)
        return

    disallowed_types = ProxyFieldProperty(IPDFOptions['disallowed_types'])
    recode_path = ProxyFieldProperty(IPDFOptions['recode_path'])
    htmldoc_path = ProxyFieldProperty(IPDFOptions['htmldoc_path'])
    htmldoc_options = ProxyFieldProperty(IPDFOptions['htmldoc_options'])


class PDFControlPanel(ControlPanelForm):

    label = _(u'label_controlpanel', default=u"PDF book settings")
    description = _(u'help_controlpanel', default=u"Your site wide options for PDF book")
    form_name = label

    form_fields = form.FormFields(IPDFOptions)
