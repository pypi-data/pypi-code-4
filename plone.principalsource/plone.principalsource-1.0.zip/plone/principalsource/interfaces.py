from zope.schema.interfaces import ITokenizedTerm
from zope import schema

class IPrincipalTerm(ITokenizedTerm):
    """A tokenised term that knows whether it refers to a user or a group.
    """
    
    type = schema.Choice(title=u"Type", values=('user', 'group',))