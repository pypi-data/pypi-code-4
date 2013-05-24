from ftw.topics.interfaces import ITopic
from plone.dexterity.content import Container
from plone.directives.form import Schema
from zope.interface import implements


class ITopicSchema(Schema):
    pass


class Topic(Container):
    implements(ITopic)
