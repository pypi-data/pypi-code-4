from Acquisition import aq_inner

from zope.interface import Interface, implements

from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from plone.memoize.instance import memoize
from raptus.article.core import RaptusArticleMessageFactory as _
from raptus.article.core import interfaces
from raptus.article.maps.interfaces import IMarkers, IMap, IMaps, IMarker
from raptus.article.maps.browser.maps import IMapsFull, IMapsLeft, IMapsRight

class View(BrowserView):
    """Map view
    """
    template = ViewPageTemplateFile('view.pt')
    
    def __call__(self):
        return self.template()
    
    @property
    @memoize
    def markers(self):
        context = aq_inner(self.context)
        manageable = interfaces.IManageable(self.context)
        items = manageable.getList(IMarkers(context).getMarkers())
        for item in items:
            item.update({'uid': item['brain'].UID,
                         'title': item['brain'].Title,
                         'description': item['brain'].Description,
                         'text': item['obj'].getText(),
                         'longitude': item['obj'].getLongitude(),
                         'latitude': item['obj'].getLatitude()})
        return items

class IHelperView(Interface):
    """ Helper view
    """
    
    def hasMaps():
        """ Whether a map is available or not
        """

class HelperView(BrowserView):
    """ Used for a python expression in the javascript registry. its
        turn off google map api if it not used.
    """
    implements(IHelperView)
    
    def hasMaps(self):
        """ Whether a map is available or not
        """
        return (
            IMap.providedBy(self.context) or
            IMarker.providedBy(self.context) or
            IMapsFull.providedBy(self.context) or 
            IMapsLeft.providedBy(self.context) or 
            IMapsRight.providedBy(self.context) or
            IMaps.providedBy(self.context))
