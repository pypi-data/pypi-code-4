from zope.interface import implements
from zope.component import adapts

from archetypes.schemaextender.interfaces import (ISchemaExtender, IOrderableSchemaExtender,
                                                    IBrowserLayerAwareExtender)
from archetypes.schemaextender.field import ExtensionField
from archetypes.markerfield import InterfaceMarkerField

from Products.ATContentTypes.configuration import zconf
from Products.Archetypes.atapi import AnnotationStorage
from Products.Archetypes.atapi import (TextField, IntegerField,
                                        BooleanField, StringField,
                                        ReferenceField)
from Products.Archetypes.atapi import (BooleanWidget, TextAreaWidget, InAndOutWidget,
                                        RichWidget, IntegerWidget, StringWidget)
from Products.ATContentTypes.interface import IATLink
from Products.ATReferenceBrowserWidget.ATReferenceBrowserWidget import ReferenceBrowserWidget

from collective.blogging.interfaces import (IBloggable, IPostable, IBlogMarker,
                                            IEntryMarker, IBloggingSpecific)
from collective.blogging import _
from collective.blogging import BLOG_PERMISSION, SHARING_PROVIDERS


class ExTextField(ExtensionField, TextField):
    """ A text field """

class ExBooleanField(ExtensionField, BooleanField):
    """ A boolean field """

class ExIntegerField(ExtensionField, IntegerField):
    """ An integer field """

class ExStringField(ExtensionField, StringField):
    """ A string field """

class ExtReferenceField(ExtensionField, ReferenceField):
    """A Reference field  """

class BlogExtender(object):
    """ Add blog configuration fields to all bloggable content. """
    adapts(IBloggable)
    implements(IOrderableSchemaExtender, IBrowserLayerAwareExtender)

    layer = IBloggingSpecific
    
    fields = [
        InterfaceMarkerField("blog_folder",
            schemata = "blog",
            write_permission = BLOG_PERMISSION,
            languageIndependent = True,
            interfaces = (IBlogMarker,),
            widget = BooleanWidget(
                label = _(u"label_blog_enabled",
                    default=u"Blog enabled"),
                description = _(u"help_blog_enabled",
                    default=u"Tick to enable / disable blog behaviour."),
            ),
        ),
        
        ExBooleanField("enable_full",
            schemata = u'blog',
            languageIndependent = True,
            default = False,
            write_permission = BLOG_PERMISSION,
            widget = BooleanWidget(
                label = _(u"label_full_view", default=u"Full view"),
                description = _(u"help_full_view",
                    default = u"Tick this checkbox to display entry body text in the blog view."),
            ),        
        ),
        
        ExBooleanField("show_header",
            schemata = u'blog',
            languageIndependent = True,
            default = True,
            write_permission = BLOG_PERMISSION,
            widget = BooleanWidget(
                label = _(u"label_show_header", default=u"Show header"),
                description = _(u"help_show_header",
                    default = u"If unchecked, blog's title and description will be hidden in the blog view."),
            ),        
        ),
        
        ExIntegerField("perex_length",
            schemata = u'blog',
            languageIndependent = True,
            default = 200,
            write_permission = BLOG_PERMISSION,
            widget = IntegerWidget(
                label = _(u"label_perex_length",
                    default=u"Perex length"),
                description = _(u"help_perex_length",
                    default = u"You can set maximal length of entry's description displayed in blog view. " + \
                               "Note: This doesn't affect blog view if Full view option above is enabled."),
            ),
        ),
        
        ExIntegerField("batch_size",
            schemata = u'blog',
            languageIndependent = True,
            default = 10,
            write_permission = BLOG_PERMISSION,
            widget = IntegerWidget(
                label = _(u"label_batch_size",
                    default=u"Batch size"),
                description = _(u"help_batch_size",
                    default = u"Enter how many blog entries should be listed per page in the blog view."),
            ),
        ),
                        
        ExTextField('blog_text',
            schemata = u'blog',
            languageIndependent = False,
            required=False,
            searchable=True,
            primary=False,
            write_permission = BLOG_PERMISSION,
            storage = AnnotationStorage(migrate=True),
            validators = ('isTidyHtmlWithCleanup',),
            #validators = ('isTidyHtml',),
            default_output_type = 'text/x-html-safe',
            widget = RichWidget(
                condition="python:not object.getField('text')",
                description = '',
                label = _(u'label_blog_text', default=u'Blog Text'),
                rows = 25,
                allow_file_upload = zconf.ATDocument.allow_document_upload
            ),
        ),
        
        ExStringField("enable_sharing",
            schemata = u'blog',
            languageIndependent = True,
            write_permission = BLOG_PERMISSION,
            enforceVocabulary = True,
            vocabulary = SHARING_PROVIDERS.keys(),
            widget = InAndOutWidget(
                label = _(u"Enable sharing"),
                description = _(u"Select enabled sharing services."),
            ),
        ),
    ]

    def __init__(self, context):
        self.context = context

    def getFields(self):
        return self.fields
    
    def getOrder(self, original):
        blog = original['blog']
        blog.remove('blog_folder')
        blog.insert(0, 'blog_folder')
        return original


class EntryExtender(object):
    """ Add a new marker field to all possible entry types. """
    adapts(IPostable)
    implements(IOrderableSchemaExtender, IBrowserLayerAwareExtender)

    layer = IBloggingSpecific

    fields = [
        InterfaceMarkerField("blog_entry",
            schemata = "blog",
            write_permission = BLOG_PERMISSION,
            languageIndependent = True,
            interfaces = (IEntryMarker,),
            widget = BooleanWidget(
                label = _(u"label_blog_entry",
                    default=u"Blog Entry"),
                description = _(u"help_blog_entry_marker",
                    default=u"Mark this content as blog entry."),
            ),
        ),
        
        ExStringField("blogger_name",
            schemata = u'blog',
            languageIndependent = True,
            default = '',
            write_permission = BLOG_PERMISSION,
            widget = StringWidget(
                label = _(u"label_blogger_name",
                    default = u"Blogger's name"),
                description = _(u"help_blogger_name",
                    default = u"Enter blogger's name if you're posting entry of different person."),
            ),
        ),
        
        ExtReferenceField('blogger_bio',
            schemata = u'blog',
            required = False,
            storage = AnnotationStorage(),
            languageIndependent = True,
            keepReferencesOnCopy = True,
            multiValued=False,
            relationship='bloggersBioPage',
            widget = ReferenceBrowserWidget(
                label=_(u"Blogger's bio"),
                description=_(u"Select a document with blogger's bio information." ),
                force_close_on_insert=1,
                hide_inaccessible=True,
            ),
        ),
    ]

    def __init__(self, context):
        self.context = context

    def getFields(self):
        return self.fields
    
    def getOrder(self, original):
        blog = original['blog']
        blog.remove('blog_entry')
        blog.insert(0, 'blog_entry')
        return original



class LinkExtender(object):
    """ Add a new marker field to all ATLink based types. """
    adapts(IATLink)
    implements(ISchemaExtender, IBrowserLayerAwareExtender)

    layer = IBloggingSpecific

    fields = [

        ExTextField('embedCode',
            schemata = "blog",
            write_permission = BLOG_PERMISSION,
            default='',
            default_content_type = 'text/plain',
            allowable_content_types = ('text/plain',),
            widget=TextAreaWidget(
                label=_(u'label_embed', default=u'Embed'),
                description=_(u'help_embed',
                              default=u'Paste embed code for example youtube, google or other video content.'),
            ),
        ),
    ]

    def __init__(self, context):
        self.context = context

    def getFields(self):
        return self.fields
