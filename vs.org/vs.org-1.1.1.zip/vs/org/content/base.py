################################################################
# vs.org (C) 2011, Veit Schiele
################################################################

# $Id$

"""
Definition of the Base content type
"""

import vs.org.validators 

from zope.interface import implements

from compatible import atapi
from Products.ATContentTypes.content import base
from Products.ATContentTypes.content import schemata
from Products.ATContentTypes.lib.constraintypes import ConstrainTypesMixinSchema
from archetypes.referencebrowserwidget.widget import ReferenceBrowserWidget
from Products.validation import V_REQUIRED

# -*- Message Factory Imported Here -*-
from .. import orgMessageFactory as _

from ..interfaces import IBase
from ..config import PROJECTNAME
from numbers import NumbersMixin

from AccessControl import ClassSecurityInfo
from Products.CMFCore.utils import getToolByName
from Products.Archetypes.atapi import DisplayList

from Products.DataGridField import DataGridField, DataGridWidget, FixedRow
from Products.DataGridField.Column import Column
from Products.DataGridField.SelectColumn import SelectColumn
from Products.DataGridField.CheckboxColumn import CheckboxColumn

BaseSchema = schemata.ATContentTypeSchema.copy() + atapi.Schema((

    # -*- Your Archetypes field definitions here ... -*-

    atapi.ReferenceField(
        name='imageReference',
        keepReferencesOnCopy=1,
        languageIndependent=1,
        widget=ReferenceBrowserWidget(
            show_review_state=1,
            allow_sorting=1,
            label=_(u'image_reference',),
        ),
        allowed_types=('Image',),
        multiValued=0,
        relationship='withImage'
    ),

    atapi.StringField(
        'url',
        storage=atapi.AnnotationStorage(),
        widget=atapi.StringWidget(
            label=_(u"label_url"),
            description=_(u"help_url"),
        ),
        validators=('isURL',),
    ),

    atapi.StringField(
        'email',
        required=True,
        storage=atapi.AnnotationStorage(),
        widget=atapi.StringWidget(
            label=_(u"label_email"),
            description=_(u"help_email"),
        ),
        validators=('isEmail',),
    ),

    DataGridField(
        'numbers',
        storage=atapi.AnnotationStorage(),
        default=(),
        fixed_rows = [
            FixedRow(keyColumn='type', initialData=dict(type='', externally_visible=False, number='')),
        ],
        columns=('type', 'number', 'externally_visible'),
        widget=DataGridWidget(
            label=_(u"label_numbers"),
            description=_(u"help_numbers"),
            columns = {
                   'type': SelectColumn(_(u'label_number_type'), vocabulary='getNumbersVocabulary'),
                   'number': Column(_(u'label_number')),
                   'externally_visible': CheckboxColumn(_(u'label_externally_visible')),
            }
        ),
    ),

))

# Set storage on fields copied from ATContentTypeSchema, making sure
# they work well with the python bridge properties.

BaseSchema['title'].storage = atapi.AnnotationStorage()
BaseSchema['description'].storage = atapi.AnnotationStorage()

schemata.finalizeATCTSchema(BaseSchema, moveDiscussion=False)

