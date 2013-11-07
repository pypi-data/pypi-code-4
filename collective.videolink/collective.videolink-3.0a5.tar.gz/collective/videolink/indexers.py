from plone.indexer.decorator import indexer
from collective.videolink.utility import add_thumbnail
from Products.ATContentTypes.interface import IATLink

@indexer(IATLink)
def videolink_thumbnail(object, **kw):
     return add_thumbnail(object,'index event')
