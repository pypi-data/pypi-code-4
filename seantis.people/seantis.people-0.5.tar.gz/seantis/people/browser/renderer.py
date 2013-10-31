""" Provides a fast renderer for schema fields. Since this renderer is used
on lists and tables and therefore called many times in a request the following
options were not chosen:

z3c.form display mode rendering - too complicated, hard to customize and slow
zpt templates - quite a bit slower because of features we don't need

The snippets rendered here so simple that string.Template can be used which
is by far the fastest way of doing templates in python.

"""

import string

from zope.schema import getFields
from plone.namedfile.field import NamedBlobImage, NamedImage

from seantis.plonetools.schemafields import Email, Website


class EmailFieldRenderer(object):

    template = string.Template(u'<a href="mailto:${url}">${url}</a>')

    def __call__(self, context, field):
        return self.template.substitute(url=getattr(context, field))


class WebsiteFieldRenderer(object):

    template = string.Template(u'<a href="${url}" target="_blank">${url}</a>')

    def __call__(self, context, field):
        return self.template.substitute(url=getattr(context, field))


class ImageRenderer(object):

    template = string.Template(u'<img src="${url}" />')

    def __call__(self, context, field):
        img = getattr(context, field)
        if img:
            url = '/'.join((context.getURL(), '@@images', field, 'thumb'))
            return self.template.substitute(url=url)
        else:
            return u''


renderers = {
    Email: EmailFieldRenderer(),
    Website: WebsiteFieldRenderer(),
    NamedBlobImage: ImageRenderer(),
    NamedImage: ImageRenderer()
}


class Renderer(object):

    def __init__(self, schema):
        self.schema = schema
        self.fields = getFields(schema)

    def render(self, context, field):
        fieldtype = type(self.fields.get(field, None))
        return renderers.get(fieldtype, getattr)(context, field)
