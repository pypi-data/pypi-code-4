from zope.interface import implements
from zope.component import getMultiAdapter

from Products.Archetypes import atapi
from Products.CMFCore.utils import getToolByName
from archetypes.schemaextender.field import ExtensionField

from raptus.article.table.interfaces import IType

class StringField(ExtensionField, atapi.StringField):
    """ String Extension Field
    """

class TextField(ExtensionField, atapi.TextField):
    """ Text Extension Field
    """

class FileField(ExtensionField, atapi.FileField):
    """ File Extension Field
    """

class ImageField(ExtensionField, atapi.ImageField):
    """ Image Extension Field
    """

class TextType(object):
    """ The text type renders plain text
    """
    implements(IType)
    def structure(self):
        return False
    def modifier(self, value, obj, col):
        return value
    def fields(self, name, label):
        return [
            StringField(name,
                required=False,
                searchable=True,
                storage = atapi.AnnotationStorage(),
                widget = atapi.StringWidget(
                    description = '',
                    label=label
                ),
            ),]
    def widget(self, name):
        return '<input type="text" name="%s" value="" />' % name

class LinkType(object):
    """ The link type renders a link
    """
    implements(IType)
    def structure(self):
        return True
    def modifier(self, value, obj, col):
        label = obj.Schema()[col['name']+'_label'].get(obj)
        if not value or value == 'http://':
            if label:
                return label
            return None
        if not label:
            label = value
        return '<a href="%s">%s</a>' % (value, label)
    def fields(self, name, label):
        return [
            StringField(name,
                required=False,
                searchable=True,
                storage = atapi.AnnotationStorage(),
                default = "http://",
                widget = atapi.StringWidget(
                    description = '',
                    label=label
                ),
            ),
            StringField(name+'_label',
                required=False,
                searchable=True,
                storage = atapi.AnnotationStorage(),
                widget = atapi.StringWidget(
                    description = '',
                    label=label+' (Label)'
                ),
            ),]
    def widget(self, name):
        return '<input type="text" name="%s" value="http://" /> <input type="text" name="%s" value="" />' % (name, name.replace(':records', '_label:records'))

class HTMLType(object):
    """ The html type renders html
    """
    implements(IType)
    def structure(self):
        return True
    def modifier(self, value, obj, col):
        return value
    def fields(self, name, label):
        return [
            TextField(name,
                required=False,
                searchable=True,
                storage = atapi.AnnotationStorage(),
                validators = ('isTidyHtmlWithCleanup',),
                default_output_type = 'text/x-html-safe',
                widget = atapi.RichWidget(
                    description = '',
                    label = label,
                    rows = 25
                ),
            ),]
    def widget(self, name):
        return '<textarea name="%s"></textarea>' % name

class FileType(object):
    """ The file type renders a link to a file
    """
    implements(IType)
    def structure(self):
        return True
    def modifier(self, value, obj, col):
        if not value or not hasattr(value, 'get_size') or not value.get_size():
            return None
        label = obj.Schema()[col['name']+'_label'].get(obj)
        if not label:
            label = '<img src="file_icon.png" />'
        return '<a href="%s/at_download/%s">%s</a>' % (obj.absolute_url(), col['name'], label)
    def fields(self, name, label):
        return [
            FileField(name,
                required=False,
                storage = atapi.AnnotationStorage(),
                widget = atapi.FileWidget(
                    description = '',
                    label = label
                ),
            ),
            StringField(name+'_label',
                required=False,
                searchable=True,
                storage = atapi.AnnotationStorage(),
                widget = atapi.StringWidget(
                    description = '',
                    label=label+' (Label)'
                ),
            ),]
    def widget(self, name):
        return None

class ImageType(object):
    """ The image type renders an image
    """
    implements(IType)
    def structure(self):
        return True
    def modifier(self, value, obj, col):
        if not value or not hasattr(value, 'get_size') or not value.get_size():
            return None
        props = getToolByName(obj, 'portal_properties').raptus_article
        w, h = props.getProperty('table_thumb_width', 0), props.getProperty('table_thumb_height', 0)
        url = '%s/image' % obj.absolute_url()
        scale = None
        if w or h:
            scales = getMultiAdapter((obj, obj.REQUEST), name='images')
            scale = scales.scale(col['name'], width=(w or 100000), height=(h or 100000))
            if scale is not None:
                url = scale.url
        caption = obj.Schema()[col['name']+'_caption'].get(obj)
        img = '<img src="%s" alt="%s" />' % (url, caption)
        if scale is not None:
            w, h = props.getProperty('table_popup_width', 0), props.getProperty('table_popup_height', 0)
            scale = scales.scale(col['name'], width=(w or 100000), height=(h or 100000))
            if scale is not None:
                img = '<a href="%s" rel="lightbox" title="%s">%s</a>' % (scale.url, caption, img)
        return img
    def fields(self, name, label):
        return [
            ImageField(name,
                required=False,
                storage = atapi.AnnotationStorage(),
                widget = atapi.ImageWidget(
                    description = '',
                    label = label
                ),
            ),
            StringField(name+'_caption',
                required=False,
                searchable=True,
                storage = atapi.AnnotationStorage(),
                widget = atapi.StringWidget(
                    description = '',
                    label=label+' (Caption)'
                ),
            ),]
    def widget(self, name):
        return None
    