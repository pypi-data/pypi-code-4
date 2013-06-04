from zope.interface import implements, alsoProvides
from zope.schema.interfaces import ITitledTokenizedTerm
from plone.principalsource.interfaces import IPrincipalTerm

class PrincipalTerm(object):
    """Simple tokenized term used by SimpleVocabulary."""

    implements(IPrincipalTerm)

    def __init__(self, value, type, token=None, title=None):
        """Create a term. If token is omitted, str(value) is used.
        If title is provided, the term object provides ITitledTokenizedTerm.
        """
        self.value = value
        self.type = type
        if token is None:
            token = value
        self.token = str(token)
        self.title = title
        if title is not None:
            alsoProvides(self, ITitledTokenizedTerm)