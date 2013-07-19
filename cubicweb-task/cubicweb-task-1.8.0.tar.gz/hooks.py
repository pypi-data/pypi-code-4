from cubicweb.predicates import is_instance
from cubicweb.sobjects.notification import ContentAddedView

class TaskAddedView(ContentAddedView):
    """get notified from new tasks"""
    __select__ = is_instance('Task')
    content_attr = 'description'
