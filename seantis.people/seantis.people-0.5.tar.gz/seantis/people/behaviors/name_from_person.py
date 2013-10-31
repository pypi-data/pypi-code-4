from plone.app.content.interfaces import INameFromTitle
from zope.interface import implements
from zope.component import adapts

from seantis.plonetools import tools
from seantis.people.supermodel import get_title_fields
from seantis.people.interfaces import INameFromPerson


def on_object_modified(obj, event=None):
    """ If an object with the INameFromPerson beheavior activated is changed,
    the title needs to be changed. This does not happen automatically.

    """

    obj.setTitle(get_name_from_person(obj))


def get_name_from_person(obj):
    schema = tools.get_schema_from_portal_type(obj.portal_type)
    fields = get_title_fields(schema)

    title = u' '.join((getattr(obj, field, u'') or u'' for field in fields))

    return title.strip()


class NameFromPerson(object):
    """ Uses the fields defined as title by seantis.people.supermodel to
    generate a title for a new object.

    """
    implements(INameFromTitle)
    adapts(INameFromPerson)

    def __init__(self, context):
        pass

    def __new__(cls, context):
        title = get_name_from_person(context)
        instance = super(NameFromPerson, cls).__new__(cls)

        instance.title = title
        context.setTitle(title)

        return instance
