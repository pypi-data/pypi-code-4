# -*- coding: utf-8 -*-
from Products.CMFCore.utils import getToolByName
from Products.Five import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from collective.portlet.mybookmarks import MyBookmarksPortletMessageFactory as _


class ConfirmDeleteView(BrowserView):
    """
    A view to confirm delete
    """
    template = ViewPageTemplateFile("confirm_delete_bookmark.pt")

    def __call__(self):
        """
        """
        if not 'delete_submitted' in self.request.form.keys() or not 'bookmark_type' in self.request.form.keys() or not 'remove_bookmark' in self.request.form.keys():
            return self.doReturn(_(u'Remove bookmark: you must select a bookmark to remove from the portlet'), 'error')
        return self.template()


class ManageBookmarksView(BrowserView):
    """
    A view to manage personal bookmarks
    """
    def __call__(self):
        """
        If there is "remove_bookmark"  in the request, the passed bookmark will be removed.
        If nothing is passed, the current object will be added as a bookmark.
        If the external bookmark form is filled, the bookmark will be added in external_bookmarks property.
        """
        if 'delete_confirmed' in self.request.form.keys():
            if 'form.button.Cancel' in self.request.form.keys():
                return self.doReturn(_(u'Removal bookmark undone'), 'info')
            elif 'form.button.Delete' in self.request.form.keys() and 'bookmark_type' in self.request.form.keys():
                return self.removeBookmark(self.request.form.get('remove_bookmark', ''), self.request.form.get('bookmark_type', ''))
            else:
                return self.doReturn(_(u'Error in removal process'), 'warning')
        if not 'form.button.Add' in self.request.form.keys():
            return self.addBookmark(self.context.UID(), 'bookmarks')
        elif 'form.submitted' in self.request.form.keys():
            if not self.request.form.get('external_title') or not self.request.form.get('external_url'):
                return self.doReturn(_(u'External bookmarks: all the required fields must be filled.'), 'error')
            external_string = "%s|%s" % (self.request.form.get('external_title', ''), self.request.form.get('external_url', ''))
            return self.addBookmark(external_string, 'external_bookmarks')

    def removeBookmark(self, element, bookmark_type):
        """
        remove the bookmark from bookmark_type property
        """
        pm = getToolByName(self.context, 'portal_membership')
        user = pm.getAuthenticatedMember()
        user_bookmarks = [x for x in user.getProperty(bookmark_type, None)]
        if element in user_bookmarks:
            user_bookmarks.remove(element)
            bookmarks = tuple(user_bookmarks)
            user.setMemberProperties({bookmark_type: bookmarks})
            return self.doReturn(_(u'Bookmark removed.'), 'info')
        return self.doReturn(_(u'Bookmark not present in list.'), 'error')

    def addBookmark(self, element, bookmark_type):
        """
        Add the bookmark to bookmark_type property
        """
        pm = getToolByName(self.context, 'portal_membership')
        user = pm.getAuthenticatedMember()
        user_bookmarks = [x for x in user.getProperty(bookmark_type, None)]
        if not user_bookmarks:
            user.setMemberProperties({bookmark_type: (element,)})
            return self.doReturn(_(u'Bookmark added.'), 'info')

        if element in user_bookmarks:
            return self.doReturn(_(u'Bookmark already present.'), 'error')
        user_bookmarks.append(element)
        bookmarks = tuple(user_bookmarks)
        user.setMemberProperties({bookmark_type: bookmarks})
        return self.doReturn(_(u'Bookmark added.'), 'info')

    def doReturn(self, message, type):
        pu = getToolByName(self.context, "plone_utils")
        pu.addPortalMessage(message, type=type)
        return_url = "%s/view" % self.context.absolute_url()
        self.request.RESPONSE.redirect(return_url)
