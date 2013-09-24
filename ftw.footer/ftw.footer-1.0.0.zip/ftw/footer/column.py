from ftw.footer.interfaces import IFooterColumn
from plone.app.portlets.manager import ColumnPortletManagerRenderer
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from zope.component import adapts
from zope.interface import Interface
from zope.publisher.interfaces.browser import IBrowserView
from zope.publisher.interfaces.browser import IDefaultBrowserLayer


class FooterColumnPortletManagerRenderer(ColumnPortletManagerRenderer):

    template = ViewPageTemplateFile('column.pt')

    adapts(Interface, IDefaultBrowserLayer, IBrowserView, IFooterColumn)
