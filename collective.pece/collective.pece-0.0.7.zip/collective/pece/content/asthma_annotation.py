from plone.directives import form
from zope.schema import TextLine


class IAsthmaAnnotation(form.Schema):
    """
    """

    title = TextLine(title=u"Title", required=True)
