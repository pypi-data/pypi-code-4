from Products.CMFCore.utils import getToolByName
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from collective.portlet.mybookmarks import MyBookmarksPortletMessageFactory as _
from plone.app.portlets.portlets import base
from plone.memoize.instance import memoize
from plone.portlets.interfaces import IPortletDataProvider
from zope import schema
from zope.formlib import form
from zope.interface import implements
from collective.portlet.mybookmarks import logger


class IMyBookmarksPortlet(IPortletDataProvider):
    """
    A portlet for user bookmarks
    """
    portletTitle = schema.TextLine(title=_(u"Title of the portlet"),
                                           description=_(u"Insert the title of the portlet."),
                                           default=_("Personal bookmark"),
                                           required=True)


class Assignment(base.Assignment):
    """
    Portlet assignment
    """

    implements(IMyBookmarksPortlet)

    def __init__(self, portletTitle=''):
        self.portletTitle = portletTitle

    @property
    def title(self):
        """This property is used to give the title of the portlet in the
        "manage portlets" screen.
        """
        if self.portletTitle:
            return self.portletTitle
        return _(u"Personal bookmark")


class Renderer(base.Renderer):
    """
    Portlet renderer
    """

    render = ViewPageTemplateFile('mybookmarksportlet.pt')

    @property
    def available(self):

        pm = getToolByName(self.context, 'portal_membership')
        if pm.isAnonymousUser():
            return False
        return True

    @property
    @memoize
    def results(self):
        """
        Return a list of user bookmarks
        """
        pc = getToolByName(self.context, 'portal_catalog')
        pm = getToolByName(self.context, 'portal_membership')
        user = pm.getAuthenticatedMember()
        fullname = user.getProperty('fullname', None)
        bookmarks = [x for x in user.getProperty('bookmarks', ())]
        external_bookmarks = [x for x in user.getProperty('external_bookmarks', ())]
        bookmarks_list = []
        if bookmarks:
            portal_types = getToolByName(self.context, 'portal_types')
            portal_properties = getToolByName(self.context, 'portal_properties')
            site_properties = getattr(portal_properties, 'site_properties')
            if site_properties.hasProperty('types_not_searched'):
                search_types = [x for x
                              in portal_types.keys()
                              if x not in site_properties.getProperty('types_not_searched')]
        for bookmark in bookmarks:
            res = pc.searchResults(UID=bookmark, portal_type=search_types)
            if res:
                bookmark_dict = {}
                bookmark_dict['Title'] = res[0].Title
                bookmark_dict['Description'] = res[0].Description
                bookmark_dict['url'] = "%s/view" % res[0].getURL()
                bookmark_dict['removeValue'] = bookmark
                bookmark_dict['bookmark_type'] = 'bookmarks'
                bookmarks_list.append(bookmark_dict)

            else:
                logger.error("Bookmark '%s' for user %s: this content is not available and the bookmark will be removed" % (bookmark, fullname))
                bookmarks.remove(bookmark)
                bookmarks = tuple(bookmarks)
                user.setMemberProperties({'bookmarks': bookmarks})

        for bookmark in external_bookmarks:
            bookmark_values = bookmark.split('|')
            if len(bookmark_values) == 2:
                bookmark_infos = self.parseExternalBookmark(bookmark_values)
                if bookmark_infos:
                    bookmarks_list.append(bookmark_infos)
        bookmarks_list.sort(lambda x, y: cmp(x['Title'].lower(), y['Title'].lower()))
        return bookmarks_list

    @property
    def default_bookmarks(self):
        """
        return the list of default bookmarks set in portal_properties
        """
        portal_properties = getToolByName(self.context, 'portal_properties')
        mybookmarks_properties = getattr(portal_properties, 'mybookmarks_properties', None)
        if not mybookmarks_properties:
            return []
        default_bookmarks = mybookmarks_properties.getProperty('default_bookmarks', ())
        bookmarks_list = []
        for bookmark in default_bookmarks:
            bookmark_values = bookmark.split('|')
            if len(bookmark_values) == 2:
                bookmark_infos = {}
                if bookmark_values[1].startswith('http://'):
                    bookmark_infos = self.parseExternalBookmark(bookmark_values)
                else:
                    portal_id = self.context.portal_url.getPortalObject().getId()
                    bookmark_path = bookmark_values[1]
                    if not bookmark_path.startswith('/'):
                        bookmark_path = "/%s" % bookmark_path
                    bookmark_obj = self.context.restrictedTraverse("%s%s" % (portal_id, bookmark_path), None)
                    if bookmark_obj:
                        bookmark_infos = self.parseInternalBookmark(bookmark_obj)
                if bookmark_infos:
                    bookmarks_list.append(bookmark_infos)
        bookmarks_list.sort(lambda x, y: cmp(x['Title'].lower(), y['Title'].lower()))
        return bookmarks_list

    def parseExternalBookmark(self, bookmark_values):
        """
        get a string and parse it to return a dict with bookmark infos
        """
        bookmark_dict = {}
        bookmark_dict['Title'] = bookmark_values[0]
        bookmark_dict['url'] = bookmark_values[1]
        bookmark_dict['removeValue'] = "|". join(bookmark_values)
        bookmark_dict['bookmark_type'] = 'external_bookmarks'
        return bookmark_dict

    def parseInternalBookmarkBrain(self, bookmark):
        """
        get a brain and return a dict with bookmark infos
        """
        bookmark_dict = {}
        bookmark_dict['Title'] = bookmark.Title
        bookmark_dict['Description'] = bookmark.Description
        bookmark_dict['url'] = "%s/view" % bookmark.getURL()
        bookmark_dict['removeValue'] = bookmark.UID
        bookmark_dict['bookmark_type'] = 'bookmarks'
        return bookmark_dict

    def parseInternalBookmark(self, bookmark):
        """
        get an object and return a dict with bookmark infos
        """
        bookmark_dict = {}
        bookmark_dict['Title'] = bookmark.Title()
        bookmark_dict['Description'] = bookmark.Description()
        bookmark_dict['url'] = "%s/view" % bookmark.absolute_url()
        bookmark_dict['removeValue'] = bookmark.UID()
        bookmark_dict['bookmark_type'] = 'bookmarks'
        return bookmark_dict


class AddForm(base.AddForm):
    """
    Portlet add form.
    """
    form_fields = form.Fields(IMyBookmarksPortlet)

    def create(self, data):
        return Assignment(**data)


class EditForm(base.EditForm):
    """
    Portlet edit form.
    """
    form_fields = form.Fields(IMyBookmarksPortlet)
