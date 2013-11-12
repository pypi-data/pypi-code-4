
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
        """ A list of membership belonging to this person. """

    def memberships_by_organizations(self, organizations=None):
        """ A dictionary of memberships belonging to this person. They key
        of the dictionary is the title of the organization. """


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


class IMembership(form.Schema):

    title = schema.TextLine(
        title=_(u"Role inside organization"),
        required=True
    )

    start = schema.Date(
        title=_(u"Start of membership"),
        required=False
    )

    end = schema.Date(
        title=_(u"End of membership"),
        required=False
    )

    person = RelationChoice(
        title=_(u"Person"),
        source=ObjPathSourceBinder(object_provides=IPerson.__identifier__),
        required=True,
    )

    @invariant
    def has_valid_daterange(Membership):
        if Membership.start is None:
            return

        if Membership.end is None:
            return

        if Membership.start > Membership.end:
            raise Invalid(_(u"The membership can't end before it starts"))
