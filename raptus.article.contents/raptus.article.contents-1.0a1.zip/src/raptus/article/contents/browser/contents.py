from zope import interface

from raptus.article.listings.browser import listing

from raptus.article.core import RaptusArticleMessageFactory as _


class IContents(interface.Interface):
    """ Marker interface for the contents viewlet
    """


class Component(listing.ComponentLeft):
    """ Component which lists the articles as a table of contents
    """

    title = _(u'Contents')
    description = _(u'List of the contained articles as a table of contents.')
    image = '++resource++contents.gif'
    interface = IContents
    viewlet = 'raptus.article.contents'


class Viewlet(listing.ViewletLeft):
    """ Viewlet listing the articles as a table of contents
    """
    title = _(u'More about this topic')
    cssClass = 'contents-listing'
    type = "contents"
    thumb_size = None
    component = "contents"
