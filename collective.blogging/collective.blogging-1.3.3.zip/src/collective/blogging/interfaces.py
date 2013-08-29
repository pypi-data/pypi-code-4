from zope.interface import Interface
from plone.theme.interfaces import IDefaultPloneLayer

class IBlog(Interface):
    """ A content which can contain blog entries, usually folders. """

class IBloggable(Interface):
    """ A content which can list blog entries, usually folders or smart folders. """

class IPostable(Interface):
    """ A content which can be posted as blog entry. """

class IBloggingView(Interface):
    """ A blogging browser view """

# markers
class IBlogMarker(Interface):
    """ A content which can act like a blog """

class IEntryMarker(Interface):
    """ A generic blog entry """

class IBloggingSpecific(IDefaultPloneLayer):
    """ A marker interface that defines a Zope 3 browser layer. """

