from cubicweb.predicates import is_instance
from cubicweb.sobjects.notification import ContentAddedView

class LinkAddedView(ContentAddedView):
    """get notified from new links"""
    __select__ = is_instance('Link')
    content_attr = 'description'
