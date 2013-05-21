import imghdr

from operator import attrgetter
from collections import namedtuple
from itertools import groupby
from urllib import urlopen
from five import grok

from collective.dexteritytextindexer import searchable
from plone.app.z3cform.wysiwyg import WysiwygFieldWidget
from plone.directives import form
from plone.namedfile.field import NamedImage as NamedImageField
from plone.namedfile import NamedImage
from zope.interface import Invalid
from zope.schema import TextLine, Text

from seantis.dir.base import item
from seantis.dir.base import core
from seantis.dir.base import utils
from seantis.dir.base.schemafields import Email, AutoProtocolURI
from seantis.dir.base.interfaces import (
    IFieldMapExtender, IDirectoryItem, IDirectoryCategorized
)

from seantis.dir.council.directory import ICouncilDirectory
from seantis.dir.council import _


class ICouncilDirectoryItem(IDirectoryItem):
    """Extends the seantis.dir.IDirectoryItem."""

    image = NamedImageField(
        title=_(u'Image'),
        required=False,
        default=None
    )

    searchable('street')
    street = TextLine(
        title=_(u'Street'),
        required=False,
        default=u''
    )

    searchable('zipcode')
    zipcode = TextLine(
        title=_(u'Zipcode'),
        required=False,
        default=u''
    )

    searchable('city')
    city = TextLine(
        title=_(u'Town'),
        required=False,
        default=u''
    )

    searchable('phone')
    phone = TextLine(
        title=_(u'Phone'),
        required=False,
        default=u''
    )

    searchable('fax')
    fax = TextLine(
        title=_(u'Fax'),
        required=False,
        default=u''
    )

    searchable('url')
    url = AutoProtocolURI(
        title=_(u'Internet Address'),
        required=False,
        default=None
    )

    searchable('email')
    email = Email(
        title=_(u'Email'),
        required=False,
        default=u''
    )

    searchable('information')
    form.widget(information=WysiwygFieldWidget)
    information = Text(
        title=_(u'Information'),
        required=False,
        default=u''
    )


# Ensure that the uploaded image at least has an image header.
@form.validator(field=ICouncilDirectoryItem['image'])
def validate_image(value):
    if not value:
        return

    if not imghdr.what(value.filename, value.data):
        raise Invalid(_(u'Unknown image format'))


class CouncilDirectoryItem(item.DirectoryItem):

    def address_components(self):
        if self.street:
            yield self.street

        if self.zipcode or self.city:
            yield ', '.join((self.zipcode, self.city))

        if self.email:
            yield '<a href="mailto:%(m)s">%(m)s</a>' % {'m': self.email}

        if self.url:
            yield '<a href="%(u)s">%(u)s</a>' % {'u': self.url}

    @property
    def address_lines(self):
        return '\n'.join('<li>%s</li>' % c for c in self.address_components())


class View(core.View):
    """Default view of a seantis.dir.council item."""
    grok.context(ICouncilDirectoryItem)
    grok.require('zope2.View')

    template = grok.PageTemplateFile('templates/item.pt')

    def tags(self):
        directory = self.context.aq_inner.aq_parent

        labels = directory.labels()
        descriptions = directory.descriptions()

        tags = []

        Tag = namedtuple('ItemTag', ['label', 'value', 'description'])
        categorized = IDirectoryCategorized(self.context)

        for category in sorted(descriptions):
            values = getattr(categorized, category) or []

            for value in sorted(utils.flatten(values)):
                if value in descriptions[category]:
                    desc = descriptions[category][value]
                else:
                    desc = None

                tags.append(Tag(labels[category], value, desc))

        # why u no accept generators zpt???
        result = {}

        for group, values in groupby(tags, attrgetter('label')):
            result[group] = list(values)

        return result


class ExtendedDirectoryItemFieldMap(grok.Adapter):
    """Adapter extending the import/export fieldmap of
    seantis.dir.council.item.

    """
    grok.context(ICouncilDirectory)
    grok.provides(IFieldMapExtender)

    def __init__(self, context):
        self.context = context

    def extend_import(self, itemmap):
        itemmap.typename = 'seantis.dir.council.item'
        itemmap.interface = ICouncilDirectoryItem

        extended = [
            'street',
            'zipcode',
            'city',
            'phone',
            'fax'
        ]

        itemmap.add_fields(extended, len(itemmap))

        # this should be temporary affair
        def on_object_add(obj, record):
            url = record[7]

            if url.startswith('http://kantonsrat'):
                result = urlopen(url + '/@@images/image')

                if result.getcode() == 200:
                    obj.image = NamedImage(result.read(), filename=u'image')

        itemmap.on_object_add = on_object_add
