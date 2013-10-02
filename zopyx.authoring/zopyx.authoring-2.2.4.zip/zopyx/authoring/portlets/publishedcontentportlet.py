#####################################################################
# zopyx.authoring
# (C) 2010, ZOPYX Limited, D-72070 Tuebingen. All rights reserved
#####################################################################


import lxml.html

from zope.interface import Interface
from zope.interface import implements

from plone.app.portlets.portlets import base
from plone.portlets.interfaces import IPortletDataProvider

from plone.memoize import instance
from zope import schema
from zope.formlib import form
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Acquisition import aq_inner, aq_parent

from zopyx.authoring import authoringMessageFactory as _
from zopyx.smartprintng.plone import xpath_query

from zope.i18nmessageid import MessageFactory
__ = MessageFactory("plone")

class IPublishedContentPortlet(IPortletDataProvider):
    """A portlet

    It inherits from IPortletDataProvider because for this portlet, the
    data that is being rendered and the portlet assignment itself are the
    same.
    """

    # some_field = schema.TextLine(title=_(u"Some field"),
    #                              description=_(u"A field to use"),
    #                              required=True)


class Assignment(base.Assignment):
    """Portlet assignment.

    This is what is actually managed through the portlets UI and associated
    with columns.
    """

    implements(IPublishedContentPortlet)

    # TODO: Set default values for the configurable parameters here

    # some_field = u""

    # TODO: Add keyword parameters for configurable parameters here
    # def __init__(self, some_field=u''):
    #    self.some_field = some_field

    def __init__(self):
        pass

    @property
    def title(self):
        """This property is used to give the title of the portlet in the
        "manage portlets" screen.
        """
        return __(u"PublishedContentPortlet")


class Renderer(base.Renderer):
    """Portlet renderer.

    This is registered in configure.zcml. The referenced page template is
    rendered, and the implicit variable 'view' will refer to an instance
    of this class. Other methods can be added and referenced in the template.
    """

    render = ViewPageTemplateFile('publishedcontentportlet.pt')

    @instance.memoize
    def getPdfFiles(self):
        return [b for b in aq_parent(aq_inner(self.context)).getFolderContents() 
                if b.getId.endswith('.pdf')] 

    @instance.memoize
    def haveEPUB(self):
        parent = aq_parent(aq_inner(self.context))
        return [b for b in parent.getFolderContents() 
                if b.getId == 'index.epub'] 

    @instance.memoize
    def haveS5(self):
        parent = aq_parent(aq_inner(self.context))
        return 'index_s5.html' in parent.objectIds()

    def folderURL(self):
        """ Return URL of parent folder """
        parent = aq_parent(aq_inner(self.context))
        return parent.absolute_url()

    def getObjSize(self, id):
        parent = aq_parent(aq_inner(self.context))
        return parent[id].getObjSize()

    @instance.memoize
    def getTableOfContents(self):
        
        actual_url = self.request.ACTUAL_URL
        parent = aq_parent(aq_inner(self.context))
        result = list()
        brains = parent.getFolderContents({'portal_type' : 'AuthoringPublishedDocument',
                                           'sort_on' : 'getObjPositionInParent'})
        if len(brains) == 1:
            h_tags = ('h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'h7', 'h8')
        else:
            h_tags = ('h2', 'h3', 'h4', 'h5', 'h6', 'h7', 'h8')

        for brain in brains:
            obj = brain.getObject()
            links = list()
            if obj.getId() == self.context.getId():
                html = unicode(obj.getText(), 'utf-8')
                root = lxml.html.fromstring(html)
                for i, tag in enumerate(root.xpath(xpath_query(h_tags))):
                    text = tag.text_content()
                    level = int(tag.tag[-1])
                    id = tag.get('id')
                    links.append(dict(level=level,
                                      href='%s#%s' % (actual_url, id),
                                      index=i,
                                      text=text))

            css_classes = obj.getId()==self.context.getId() and 'toc-table toc-table-active' or 'toc-table'
            result.append(dict(id=obj.getId(), 
                               title=obj.Title(), 
                               url=obj.absolute_url(),
                               css_classes=css_classes,
                               links=links))
        return result


class AddForm(base.AddForm):
    """Portlet add form.

    This is registered in configure.zcml. The form_fields variable tells
    zope.formlib which fields to display. The create() method actually
    constructs the assignment that is being added.
    """
    form_fields = form.Fields(IPublishedContentPortlet)

    def create(self, data):
        return Assignment(**data)


# NOTE: IF this portlet does not have any configurable parameters, you can
# remove this class definition and delete the editview attribute from the
# <plone:portlet /> registration in configure.zcml

class EditForm(base.EditForm):
    """Portlet edit form.

    This is registered with configure.zcml. The form_fields variable tells
    zope.formlib which fields to display.
    """
    form_fields = form.Fields(IPublishedContentPortlet)
