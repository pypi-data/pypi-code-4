from collections import defaultdict

from plone import api
from zope.interface import implements

from seantis.plonetools import tools
from seantis.people.interfaces import IPerson


class Person(object):
    implements(IPerson)

    def __init__(self, context):
        self.context = context

    def memberships(self):
        catalog = api.portal.get_tool(name='portal_catalog')
        memberships = catalog(portal_type='seantis.people.membership')

        return memberships

    def memberships_by_organization(self, organizations=None):
        result = defaultdict(list)

        for membership in self.memberships():
            organization = tools.get_parent(membership).title

            if organizations is None or organization in organizations:
                result[organization].append(membership)

        return result
