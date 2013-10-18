from zope.interface import implements, Interface
from Products.Five import BrowserView
from zope.traversing.browser.absoluteurl import absoluteURL

import urllib2

class Iclickmap_anonymView(Interface):
    """
    clickmap_anonym view interface
    """

class clickmap_anonymView(BrowserView):
    """
    clickmap_anonym browser view
    """
    implements(Iclickmap_anonymView)

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self):
        """ returning the context as anonymous """
        url = absoluteURL(self.context, self.request)
        response = urllib2.urlopen('%s?show_clickmap_output=true' %(url))
        return response.read()
