from plone.app.content.interfaces import INameFromTitle
from zope.interface import implements
from zope.component import adapts

from seantis.plonetools import tools
from seantis.people.supermodel import get_title_fields
from seantis.people.interfaces import INameFromPerson


class NameFromPerson(object):
    """ Uses the fields defined as title by seantis.people.supermodel to
    generate a title for a new object.

    """
    implements(INameFromTitle)
    adapts(INameFromPerson)

    def __init__(self, context):
        pass

    def __new__(cls, context):
        schema = tools.get_schema_from_portal_type(context.portal_type)
        fields = tools.order_fields_by_schema(
            get_title_fields(schema), schema
        )

        title = ' '.join(
            [getattr(context, field, '') or '' for field in fields]
        )
        title = title.strip()

        instance = super(NameFromPerson, cls).__new__(cls)

        instance.title = title
        context.setTitle(title)

        return instance
