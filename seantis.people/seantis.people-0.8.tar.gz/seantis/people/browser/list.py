from five import grok

from Products.CMFPlone.PloneBatch import Batch

from seantis.plonetools import tools

from seantis.people import _
from seantis.people.interfaces import IList
from seantis.people.browser import BaseView, Renderer
from seantis.people.content.list import ListFilter, LetterFilter
from seantis.people.supermodel import (
    get_schema_columns
)


class ListView(BaseView):

    permission = 'zope2.View'
    grok.require(permission)
    grok.context(IList)
    grok.name('view')

    template = grok.PageTemplateFile('templates/list.pt')
    filter_prefix = 'filter-'

    def update(self):
        if self.has_people:
            self.renderer = Renderer(self.schema)

    @property
    def has_people(self):
        return bool(self.context.used_type())

    @property
    def schema(self):
        assert self.has_people, """
            Do not use if there are no people in the list.
        """

        return self.context.used_type().lookupSchema()

    @property
    def filter(self):
        if self.letter:
            return LetterFilter(self.letter, _(u'Letter'))

        for key in self.request.keys():
            if key.startswith(self.filter_prefix):
                val = self.request[key].decode('utf-8')
                key = key.replace(self.filter_prefix, '')

                field = self.has_people and self.schema.get(key, None) or None
                title = field and field.title or u''

                return ListFilter(key, val, title)

        return None

    @property
    def letter(self):
        return self.request.get('letter', '').decode('utf-8')

    @property
    def batch_size(self):
        return int(self.request.get('b_size', self.context.people_per_page))

    @property
    def batch_start(self):
        return int(self.request.get('b_start', 0))

    def people(self):
        people = self.context.people(
            filter=self.filter,
            batch_start=self.batch_start,
            batch_size=self.batch_size
        )
        return Batch(people, self.batch_size, self.batch_start)

    def columns(self):
        return get_schema_columns(self.schema, self.context)

    def column_values(self, column):
        assert column.selectable

        people = self.context.people()
        
        unique_values = set()

        for value in (getattr(brain, column.fields[0]) for brain in people):
            if value is None:
                continue

            if isinstance(value, list):
                map(unique_values.add, value)
            else:
                unique_values.add(value)
                
        return sorted(unique_values, key=tools.unicode_collate_sortkey())

    def selected_column_value(self, column):
        assert column.selectable

        filter = self.filter

        if isinstance(filter, ListFilter) and filter.key == column.fields[0]:
            return filter.value
        else:
            return '__all__'
