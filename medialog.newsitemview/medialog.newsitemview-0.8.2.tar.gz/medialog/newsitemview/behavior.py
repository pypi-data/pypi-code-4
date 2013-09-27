from zope import schema
from plone.directives import dexterity
from plone.directives import form
from plone.autoform.interfaces import IFormFieldProvider
from zope.interface import alsoProvides
from zope.i18nmessageid import MessageFactory

_ = MessageFactory('medialog.newsitemviews')
 
class ICustomSize(form.Schema):
    """ A field where you can set the size for images"""
    newsitemsize = schema.Choice(
        title = _("label_folderimagesize", default=u"Size for image in summary view"),
        description = _("help_folderimagesize",
                      default="Choose Size"),
        vocabulary='medialog.newsitemview.ImageSizeVocabulary',
        default='mini',
    )

alsoProvides(ICustomSize, IFormFieldProvider)

