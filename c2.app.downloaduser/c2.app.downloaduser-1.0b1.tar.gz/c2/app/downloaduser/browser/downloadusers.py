# fallback to simplejson for pre python2.6
try:
    import json
except:
    import simplejson as json
from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from zope.component import getMultiAdapter, queryUtility
from zope.i18n.interfaces import ITranslationDomain
from Products.CMFCore.utils import getToolByName
from c2.app.downloaduser import DownloadUserMessageFactory as _
from c2.app.downloaduser import record


class DownloadUsersWidgetView(BrowserView):
    """ Display the download users widget. """
    render = ViewPageTemplateFile('downloadusers.pt')

    def __init__(self, context, request):
        self.context = context
        self.request = request
        self.annotations = record.setupAnnotations(self.context)

    def __call__(self):
        return self.render()

    def getStats(self):
        """
        Look up the annotation on the object and return the number of
        likes and hates
        """
        return record.getTally(self.context)

    def myDownload(self):
        return record.getMyDownload(self.context)

    def get_fullname_by_userid(self, user_id):
        mtool = getToolByName(self.context, 'portal_membership')
        member = mtool.getMemberInfo(user_id)
        if member is not None:
            out = member.get('fullname')
            if not out:
                out = user_id
            return out
        else:
            return user_id

