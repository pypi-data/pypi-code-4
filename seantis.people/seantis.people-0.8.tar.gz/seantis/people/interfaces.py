
from plone.formwidget.contenttree import ObjPathSourceBinder
from plone.directives import form

from z3c.relationfield.schema import RelationChoice

from zope import schema
from zope.interface import Interface, invariant, Invalid

from seantis.people import _


class ISeantisPeopleSpecific(Interface):
    pass


class IPersonMarker(Interface):
    pass


class IPerson(Interface):

    def memberships(self):
        """ A dictionary of membership belonging to this person, keyed by
        organization (brain or object with a title and an url)."""


class INameFromPerson(Interface):
    pass


class IList(form.Schema):
    """ A list of IPerson objects. """

    title = schema.TextLine(
        title=_(u"Name of the list of people"),
        required=True
    )

    people_per_page = schema.Int(
        title=_(u"Number of people shown on each page"),
        required=True,
        default=50
    )


class IMembershipSource(Interface):

    def memberships(self, person=None):
        """ Return a dictionary of objects providing IMembership. The key
        of the dictionary is the uuid of the organization (object with url and
        title).

        If a person object (not a brain) is given, only the memberships
        of that person are returned.
        """



class IMembership(form.Schema):

    person = RelationChoice(
        title=_(u"Person"),
        source=ObjPathSourceBinder(
            object_provides=IPersonMarker.__identifier__
        ),
        required=True,
    )

    title = schema.TextLine(
        title=_(u"Role inside organization"),
        required=False
    )

    start = schema.Date(
        title=_(u"Start of membership"),
        required=False
    )

    end = schema.Date(
        title=_(u"End of membership"),
        required=False
    )

    @invariant
    def has_valid_daterange(Membership):
        if Membership.start is None:
            return

        if Membership.end is None:
            return

        if Membership.start > Membership.end:
            raise Invalid(_(u"The membership can't end before it starts"))
