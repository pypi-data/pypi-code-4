from ftw.topics import _
from ftw.topics.interfaces import ITopicRootFinder
from plone.autoform.interfaces import IFormFieldProvider
from plone.directives.form import widget
from plone.formwidget.contenttree import MultiContentTreeFieldWidget
from plone.formwidget.contenttree import UUIDSourceBinder
from plone.formwidget.contenttree.utils import closest_content
from zope.component import getMultiAdapter
from zope.interface import Interface
from zope.interface import alsoProvides
from zope.schema import Choice
from zope.schema import List


class TopicsUUIDSourceBinder(UUIDSourceBinder):

    def __call__(self, context):
        if not self.navigation_tree_query:
            self.navigation_tree_query = {}

        finder = getMultiAdapter((context, context.REQUEST),
                                 ITopicRootFinder)
        self.navigation_tree_query['path'] = {
            'query': finder.get_topic_root_path()}

        return self.path_source(
            closest_content(context),
            selectable_filter=self.selectable_filter,
            navigation_tree_query=self.navigation_tree_query)


class ITopicSupportSchema(Interface):
    """Schema interface for the `ITopicSupport` behavior, adding
    a reference field `topics` to the content type.
    """

    widget(topics=MultiContentTreeFieldWidget)
    topics = List(
        title=_(u'label_topics', default=u'Topics'),
        value_type=Choice(
            source=TopicsUUIDSourceBinder(
                # portal_type=['ftw.topics.Topic']
                )))


alsoProvides(ITopicSupportSchema, IFormFieldProvider)
