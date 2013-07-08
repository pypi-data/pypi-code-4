from plone.app.discussion.interfaces import IConversation
from plone.app.form.widgets.uberselectionwidget import UberSelectionWidget
from plone.app.portlets.portlets import base
from plone.app.vocabularies.catalog import SearchableTextSourceBinder
from plone.portlets.interfaces import IPortletDataProvider
from Products.CMFCore.interfaces._content import ISiteRoot
from Products.CMFCore.utils import getToolByName
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from redturtle.portlet.content import ContentPortletMessageFactory as _
from string import Template
from zope import schema
from zope.component._api import getUtility
from zope.formlib import form
from zope.i18n import translate
from zope.interface import implements
import re


class IContentPortlet(IPortletDataProvider):
    """A portlet

    It inherits from IPortletDataProvider because for this portlet, the
    data that is being rendered and the portlet assignment itself are the
    same.
    """
    portletTitle = schema.TextLine(title=_(u"Title of the portlet"),
                               description=_(u"Insert the title of the portlet. If empty, the title will be the title of the object."),
                               required=False)
    showTitle = schema.Bool(title=_(u"show_title", default=u"Show title"),
                               description=_(u"Show the title of the object."),
                               required=False)

    showDescr = schema.Bool(title=_(u"Show description"),
                               description=_(u"Show the description of the object."),
                               default=False,
                               required=False)

    showText = schema.Bool(title=_(u"Show text"),
                               description=_(u"Show the formatted text of the object, if there is."),
                               default=False,
                               required=False)

    showImage = schema.Bool(title=_(u"Show image"),
                               description=_(u"Show the image of the object, if there is."),
                               default=False,
                               required=False)

    imageScale = schema.Choice(title=_(u"Image miniature"),
                               description=_(u"Select and image miniature dimension, if you want to show the image for this content. If empty will be used mini miniature."),
                               vocabulary="redturtle.portlet.content.ImageMiniaturesVocabulary",
                               required=False)

    showComments = schema.Bool(title=_(u"Show number of comments"),
                               description=_(u"Show the number of comments of the object, if they are activated."),
                               default=False,
                               required=False)

    showSocial = schema.Bool(title=_(u"Show social links"),
                               description=_(u"Show links to share this content with some social sites."),
                               default=False,
                               required=False)

    showMore = schema.Bool(title=_(u"Show more"),
                               description=_(u"Is a link to the object, to show all the informations. If checked, the title will not be clickable."),
                               required=False)

    content = schema.Choice(title=_(u"Target object"),
                            description=_(u"Find the item to show."),
                            required=True,
                            source=SearchableTextSourceBinder({}, default_query='path:'))

    portletId = schema.TextLine(title=_(u"Id of the portlet"),
                            description=_(u"Insert an Id for the portlet. If empty, the id will be the id of the object."),
                            required=False)

    portletClass = schema.TextLine(title=_(u"CSS class"),
                        description=_(u"You can add in this field a CSS class (or more classes divided by a space)."),
                        required=False)


class Assignment(base.Assignment):
    """Portlet assignment.

    This is what is actually managed through the portlets UI and associated
    with columns.
    """

    implements(IContentPortlet)
    """
    portletId, portletClass and showComments are added here, to avoid breaking old portlets
    """
    portletId = ''
    portletClass = ''
    showComments = False
    showSocial = False
    imageScale = ""

    def __init__(self, portletTitle='',
                      showTitle=False,
                      showDescr=False,
                      showText=False,
                      showImage=False,
                      imageScale="",
                      showComments=False,
                      showSocial=False,
                      showMore=False,
                      content=None,
                      portletId='',
                      portletClass=''):

        self.portletTitle = portletTitle
        self.showTitle = showTitle
        self.showDescr = showDescr
        self.showText = showText
        self.showImage = showImage
        self.imageScale = imageScale
        self.showComments = showComments
        self.showSocial = showSocial
        self.showMore = showMore
        self.content = content
        self.portletId = portletId
        self.portletClass = portletClass

    @property
    def title(self):
        """This property is used to give the title of the portlet in the
        "manage portlets" screen.
        """
        if self.portletTitle:
            return self.portletTitle
        else:
            return "Generic content portlet"


class Renderer(base.Renderer):
    """Portlet renderer.

    This is registered in configure.zcml. The referenced page template is
    rendered, and the implicit variable 'view' will refer to an instance
    of this class. Other methods can be added and referenced in the template.
    """

    render = ViewPageTemplateFile('contentportlet.pt')

    def getPortletClass(self):
        if self.data.portletClass:
            return self.data.portletClass
        else:
            return ''

    def getItem(self):
        context = self.context
        root_path = context.portal_url.getPortalObject().getPhysicalPath()
        item_path = self.data.content.split('/')
        item_url = '/'.join(root_path) + '/'.join(item_path[:-1])
        item = context.portal_catalog(path={'query': item_url, 'depth': 1}, id=item_path[-1])
        if item:
            return item[0]
        else:
            return None

    def needObj(self, item):
        if (self.data.showText or self.data.showImage or self.data.showComments or self.data.showSocial) and item:
            return item.getObject()
        else:
            return None

    def getPortletId(self, item):
        if self.data.portletId:
            return self.data.portletId
        else:
            return item.getId

    def hasImageField(self, item):
        try:
            if item.getImage():
                return True
            else:
                return False
        except AttributeError:
            return False

    def getImageScale(self):
        return self.data.imageScale or "mini"

    def getClass(self):
        if self.data.portletTitle:
            return 'portletHeader'
        else:
            return 'portletHeader hidden'

    def getItemDescription(self, item):
        portal_transforms = getToolByName(self, 'portal_transforms')
        data = portal_transforms.convert('web_intelligent_plain_text_to_html', item.Description)
        return data.getData()

    def getCommentsLen(self, item):
        """
        Return the number of comments of the object
        """
        if not item.restrictedTraverse('@@conversation_view').enabled():
            return 0
        wf = getToolByName(self.context, 'portal_workflow')
        discussions = IConversation(item)
        list_discussions = discussions.getThreads()
        num_discussions = 0
        for discuss in list_discussions:
            comment_obj = discuss['comment']
            workflow_status = wf.getInfoFor(comment_obj, 'review_state')
            if workflow_status == 'published':
                num_discussions += 1
        return num_discussions

    def getCommentsString(self, comments):
        """
        Return the text for the link, translated
        """
        if comments == 1:
            msg = 'comment'
        else:
            msg = 'comments'
        comments_msg = translate(_(msg), context=self.request)

        return "%s %s" % (str(comments), comments_msg)

    def socialProviders(self, item):
        """Returns a list of dicts with providers already
           filtered and populated"""
        if not self.socialEnabled(item):
            return []
        providers = []
        available = self.availableProviders()
        param = {}
        param['title'] = item.Title()
        param['description'] = item.Description()
        param['url'] = item.absolute_url()
        # BBB: Instead of using string formatting we moved to string Templates
        pattern = re.compile("\%\(([a-zA-Z]*)\)s")
        for provider in available:
            url_tmpl = provider.get('url', '').strip()
            if not(url_tmpl):
                continue
            url_tmpl = re.sub(pattern, r'${\1}', url_tmpl)
            provider['url'] = Template(url_tmpl).safe_substitute(param)
            providers.append(provider)
        return providers

    def socialEnabled(self, item):
        """Validates if social links should be visibles
           for this item"""
        if not self.data.showSocial or not item:
            return False
        if not self.socialLinksProduct():
            return False
        pp = getToolByName(self.context, 'portal_properties')
        if hasattr(pp, 'sc_social_bookmarks_properties'):
            enabled_portal_types = pp.sc_social_bookmarks_properties.getProperty("enabled_portal_types") or []
        else:
            enabled_portal_types = []
        return item.portal_type in enabled_portal_types

    def socialLinksProduct(self):
        """
        Check if sc.social.bookmarks is installed
        """
        quickinstaller_tool = getToolByName(self.context, 'portal_quickinstaller')
        return quickinstaller_tool.isProductInstalled('sc.social.bookmarks')

    def availableProviders(self):
        """
        Return a list of available social providers
        """
        try:
            from sc.social.bookmarks.config import all_providers
        except:
            return []
        pp = getToolByName(self.context, 'portal_properties')
        if hasattr(pp, 'sc_social_bookmarks_properties'):
            bookmark_providers = pp.sc_social_bookmarks_properties.getProperty("bookmark_providers") or []
        else:
            bookmark_providers = []
        providers = []
        for bookmarkId in bookmark_providers:
            tmp_providers = [provider for provider in all_providers if provider.get('id', '') == bookmarkId]
            if not tmp_providers:
                continue
            else:
                provider = tmp_providers[0]

            logo = provider.get('logo', '')
            url = provider.get('url', '')
            providers.append({'id': bookmarkId, 'logo': logo, 'url': url})

        return providers


class AddForm(base.AddForm):
    """Portlet add form.
    """
    
    @property
    def form_fields(self):
        """
        If sc.social.bookmarks isn't installed, omit social field
        """
        ff = form.Fields(IContentPortlet)
        ff['content'].custom_widget = UberSelectionWidget
        self.socialLinksProduct()
        if not self.socialLinksProduct():
            return ff.omit('showSocial')
        else:
            return ff

    def create(self, data):
        return Assignment(**data)

    def socialLinksProduct(self):
        portal = getUtility(ISiteRoot)
        quickinstaller_tool = getToolByName(portal, 'portal_quickinstaller')
        return quickinstaller_tool.isProductInstalled('sc.social.bookmarks')


class EditForm(base.EditForm):
    """Portlet edit form.

    If sc.social.bookmarks isn't installed, omit social field
    """
    @property
    def form_fields(self):
        '''
        '''
        ff = form.Fields(IContentPortlet)
        ff['content'].custom_widget = UberSelectionWidget
        self.socialLinksProduct()
        if not self.socialLinksProduct():
            return ff.omit('showSocial')
        else:
            return ff

    def socialLinksProduct(self):
        portal = getUtility(ISiteRoot)
        quickinstaller_tool = getToolByName(portal, 'portal_quickinstaller')
        return quickinstaller_tool.isProductInstalled('sc.social.bookmarks')
