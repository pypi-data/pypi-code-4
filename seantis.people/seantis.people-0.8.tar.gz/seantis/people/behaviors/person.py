from zope.interface import implements

from seantis.people.interfaces import IPerson
from seantis.people.behaviors.memberships import get_memberships


class Person(object):
    implements(IPerson)

    def __init__(self, context):
        self.context = context

    def memberships(self):
        return get_memberships(self.context)
