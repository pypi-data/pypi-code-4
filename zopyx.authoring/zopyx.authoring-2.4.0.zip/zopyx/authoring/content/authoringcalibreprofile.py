#####################################################################
# zopyx.authoring
# (C) 2011, ZOPYX Limited, D-72070 Tuebingen. All rights reserved
#####################################################################

"""Definition of the AuthoringCalibreProfile content type
"""

from zope.interface import implements
from AccessControl import ClassSecurityInfo

from Products.Archetypes import atapi
from Products.ATContentTypes.content import base
from Products.ATContentTypes.content import schemata
from Products.CMFCore.permissions import View

from Products.DataGridField import DataGridField, DataGridWidget, FixedRow
from Products.DataGridField.Column import Column

from zopyx.authoring import authoringMessageFactory as _
from zopyx.authoring.interfaces import IAuthoringCalibreProfile
from zopyx.authoring.config import PROJECTNAME

from util import invisibleFields
from .. import config

AuthoringCalibreProfileSchema = schemata.ATContentTypeSchema.copy() + atapi.Schema((

    DataGridField(
        'options',
        schemata='default',
        default=config.CALIBRE_DEFAULT_OPTIONS,
        allow_empty_rows=True,
        allow_oddeven=True,
        storage=atapi.AnnotationStorage(),
        columns=('name','value'),
        widget=DataGridWidget(
            label=_(u'label_calibre_options', u'Calibre options'),
            description=_(u'label_calibre_options_help', u'Calibre options'),
            visible={'edit' : 'visible', 'view' : 'visible'},
            columns = {
                    'name' : Column(_(u'label_calibre_option_name', 'Name')),
                    'value' :  Column(_(u'label_calibre_option_value', u'Value')),
            },
        ),
    ),
))

# Set storage on fields copied from ATContentTypeSchema, making sure
# they work well with the python bridge properties.


AuthoringCalibreProfileSchema['title'].storage = atapi.AnnotationStorage()
AuthoringCalibreProfileSchema['description'].storage = atapi.AnnotationStorage()
invisibleFields(AuthoringCalibreProfileSchema, 
                'description',
                'allowDiscussion', 'relatedItems', 
                'excludeFromNav', 'subject', 'location', 
                'creators', 'contributors', 'rights',
                'language', 'effectiveDate', 'expirationDate')
schemata.finalizeATCTSchema(AuthoringCalibreProfileSchema, moveDiscussion=False)

class AuthoringCalibreProfile(base.ATCTContent):
    """Authoring Environment Calibre Profile"""
    implements(IAuthoringCalibreProfile)

    meta_type = "AuthoringCalibreProfile"
    schema = AuthoringCalibreProfileSchema
    security = ClassSecurityInfo()

    title = atapi.ATFieldProperty('title')
    description = atapi.ATFieldProperty('description')

    # -*- Your ATSchema to Python Property Bridges Here ... -*-

    security.declareProtected(View, 'getCommandlineOptions')
    def getCommandlineOptions(self):
        """ Return commandline options for calibre profile """

        cmd = ''
        for d in self.getOptions():
            cmd += ' %s %s' % (d['name'], d['value'])
        return cmd

    def update_data(self, data):
        options = list()
        for line in data.split('\n'):
            line = line.strip()
            if line:
                name, value = line.split(' ' , 1)
                options.append(dict(name=name, value=value))
        self.setOptions(options)

    def get_data(self):
        result = list()
        for d in self.getOptions():
            result.append('%s %s' % (d['name'], d['value']))
        return '\n'.join(result)

atapi.registerType(AuthoringCalibreProfile, PROJECTNAME)
