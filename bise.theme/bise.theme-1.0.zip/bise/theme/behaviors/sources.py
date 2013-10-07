from zope.interface import alsoProvides
from zope import schema
from plone.directives import form, dexterity
from bise.theme import themeMessageFactory as _
from plone.app.textfield import RichText

from five import grok
from plone.namedfile.interfaces import IImageScaleTraversable

class IExtraNewsItem(form.Schema):

    resourceurl = schema.TextLine(title=_(u'Original URL of this item'),
       default=u'',
       required=False,
       )

    source = schema.Text(title=_(u'Source of this item'),
       default=u'',
       required=False,
       )

alsoProvides(IExtraNewsItem, form.IFormFieldProvider)

class IExtraFolderishPage(form.Schema, IImageScaleTraversable):

    navmenucode = RichText(title=_(u'Content to show on Navigation Menu'),
                    required=False
        )

alsoProvides(IExtraFolderishPage, form.IFormFieldProvider)
