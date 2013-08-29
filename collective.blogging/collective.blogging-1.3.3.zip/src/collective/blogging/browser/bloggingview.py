from Products.Five import BrowserView

from collective.blogging.interfaces import IBlogMarker, IEntryMarker


class BloggingView(BrowserView):
    """ A blogging helper view """

    @property
    def is_blog(self):
        return IBlogMarker.providedBy(self.context)
    
    @property
    def is_entry(self):
        return IEntryMarker.providedBy(self.context)
    
    @property
    def is_blogging(self):
        return self.is_entry or self.is_blog
