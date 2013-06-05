from zope.interface import alsoProvides, implements
from zope.component import adapts
from zope import schema
from plone.directives import form
from plone.dexterity.interfaces import IDexterityContent
from plone.autoform.interfaces import IFormFieldProvider

from plone.namedfile import field as namedfile
from z3c.relationfield.schema import RelationChoice, RelationList
from plone.formwidget.contenttree import ObjPathSourceBinder
from collective.sliderfields.interfaces import ISliderFieldsEnabled
from collective.sliderfields import MessageFactory as _
from plone.app.dexterity import MessageFactory as _pad
from Acquisition import aq_base

class ISliderImage(form.Schema, ISliderFieldsEnabled):
    """
       Marker/Form interface for Slider Image
    """
    form.fieldset('settings',
        label=_pad('Settings'),
        fields=['slider_image', 'slider_title', 'slider_description']
    )

    slider_image = namedfile.NamedBlobImage(
        title=_(u'slider_image_label', default=u'Slider Image'),
        description=_(
            u'slider_image_description', 
            default=u'Upload slider image'),
        required=False
    )

    slider_title = schema.TextLine(
        title=_(u'slider_title_label', default=u'Slider Title'),
        description=_(u'slider_title_description', 
            default=(u'If set, the slider will use this title instead'
                    ' of the content title')
        ),
        required=False
    )

    slider_description = schema.TextLine(
        title=_(u'slider_description_label', default=u'Slider Description'),
        description=_(u'slider_description_description',
            default=(u'If set, the slider will use this description instead'
                    ' of the content description'),
        ),
        required=False
    )


    # -*- Your Zope schema definitions here ... -*-

alsoProvides(ISliderImage,IFormFieldProvider)
