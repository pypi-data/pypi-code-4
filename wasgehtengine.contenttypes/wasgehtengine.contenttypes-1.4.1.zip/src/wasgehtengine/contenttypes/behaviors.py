from plone.app.content.interfaces import INameFromTitle
from zope.interface import implements
from zope.interface import Interface
from zope.component import adapts
from Products.CMFCore.interfaces import IDublinCore
from plone.dexterity.interfaces import IDexterityContent

class INameFromTitleDateVenue(Interface):
    """ Interface to adapt to INameFromTitle """

class NameFromTitleDateVenue(object):
    """ Adapter to INameFromTitle """
    implements(INameFromTitle)
    adapts(IDexterityContent)

    def __init__(self, context):
        self.context = context
        pass

    def __new__(cls, context):
        inst = super(NameFromTitleDateVenue, cls).__new__(cls)

        inst.title = generate_id(context.title, context.start, context.venue)
        context.setTitle(context.title)

        return inst
    
def generate_id(title, start, venue):
    venue_path = venue.to_object.absolute_url()
    venue_id = venue_path.split('/')[-1]
    datetime = start.strftime('%Y-%m-%d-%H-%M')
        
    return u'%s-%s-%s' % (title, datetime, venue_id)