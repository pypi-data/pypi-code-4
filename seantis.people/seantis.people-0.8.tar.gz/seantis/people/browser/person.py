from five import grok

from plone.namedfile.field import NamedBlobImage, NamedImage

from seantis.plonetools import tools
from seantis.people.supermodel import security, get_detail_fields
from seantis.people.interfaces import IPersonMarker
from seantis.people.browser import BaseView, Renderer


class PersonView(BaseView):

    permission = 'zope2.View'
    grok.require(permission)
    grok.context(IPersonMarker)
    grok.name('view')

    template = grok.PageTemplateFile('templates/person.pt')

    types_without_label = (
        NamedBlobImage,
        NamedImage
    )

    def update(self):
        self.renderer = Renderer(self.schema)

    @property
    def schema(self):
        return tools.get_schema_from_portal_type(self.context.portal_type)

    def fields(self, position):
        has_access = lambda field: security.has_read_access(
            self.schema, field, self.context
        )
        fields = get_detail_fields(self.schema).get(position)

        if not fields:
            return []

        return [f for f in fields if has_access(f)]

    def get_field_title(self, field):
        if field in self.schema:
            if type(self.schema[field]) in self.types_without_label:
                return u''

            return self.schema[field].title
        else:
            return field

    def visible_positions(self):
        positions = ('top', 'left', 'right', 'bottom')
        return [
            p for p in positions if any(
                getattr(self.context, f) for f in self.fields(p)
            )
        ]

    def split_screen(self):
        return set(('left', 'right')).issubset(set(self.visible_positions()))
