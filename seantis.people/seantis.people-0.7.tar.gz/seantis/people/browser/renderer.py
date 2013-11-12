""" Provides a fast renderer for schema fields. Since this renderer is used
on lists and tables and therefore called many times in a request the following
options were not chosen:

z3c.form display mode rendering - too complicated, hard to customize and slow
zpt templates - quite a bit slower because of features we don't need

The snippets rendered here so simple that string.Template can be used which
is by far the fastest way of doing templates in python.

"""

import string

from zope.schema import getFields, Text, Tuple, List, Set, FrozenSet
from plone.namedfile.field import NamedBlobImage, NamedImage
from plone.app.textfield import RichText
from Products.ZCatalog.interfaces import ICatalogBrain

from seantis.plonetools.schemafields import Email, Website


class EmailFieldRenderer(object):

    template = string.Template(u'<a href="mailto:${url}">${url}</a>')

    def __call__(self, context, field):
        return self.template.substitute(url=getattr(context, field))


class WebsiteFieldRenderer(object):

    template = string.Template(u'<a href="${url}" target="_blank">${url}</a>')

    def __call__(self, context, field):
        return self.template.substitute(url=getattr(context, field))


class TextRenderer(object):

    def __call__(self, context, field):
        return '<br />'.join(getattr(context, field, u'').splitlines())


class RichTextRenderer(object):

    def __call__(self, context, field):
        return getattr(context, field).output


class ListRenderer(object):

    def __call__(self, context, field):
        return u', '.join(getattr(context, field, tuple()))


class ImageRenderer(object):

    template = string.Template(u'<img src="${url}" />')

    def __call__(self, context, field):
        img = getattr(context, field)
        if img:
            if ICatalogBrain.providedBy(context):
                baseurl = context.getURL()
            else:
                baseurl = context.absolute_url()

            url = '/'.join((baseurl, '@@images', field, 'thumb'))

            return self.template.substitute(url=url)
        else:
            return u''


# This is not the best way to match objects to classes, but it sure is the
# fastest. Checking through isinstance would require going through a list.
# Since that can easily happen more than a thousand times in a request it's
# better to be fast than to be right.
renderers = {
    Email: EmailFieldRenderer(),
    Website: WebsiteFieldRenderer(),
    NamedBlobImage: ImageRenderer(),
    NamedImage: ImageRenderer(),
    Text: TextRenderer(),
    RichText: RichTextRenderer(),
    Tuple: ListRenderer(),
    List: ListRenderer(),
    Set: ListRenderer(),
    FrozenSet: ListRenderer(),
    list: ListRenderer(),
    set: ListRenderer(),
    tuple: ListRenderer()
}


class Renderer(object):

    def __init__(self, schema):
        self.schema = schema
        self.fields = getFields(schema)

    def render(self, context, field):
        fieldtype = type(self.fields.get(field, getattr(context, field, None)))
        return renderers.get(fieldtype, getattr)(context, field)
