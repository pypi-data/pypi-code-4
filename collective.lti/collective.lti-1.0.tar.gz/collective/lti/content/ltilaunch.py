from Products.ATContentTypes.atct import ATContentTypeSchema
from Products.Archetypes.atapi import Schema
from Products.Archetypes.atapi import StringField, StringWidget
from Products.ATContentTypes.atct import ATCTContent
from Products.Archetypes.atapi import registerType
from zope.interface import implements

from collective.lti import ltiMessageFactory as _
from collective.lti.interfaces import ILtiLaunchParams
from collective.lti.config import PROJECTNAME


# Schema Definition
schema = ATContentTypeSchema.copy() + Schema((

    StringField('secret',
                required=True,
                widget=StringWidget(
                    label_msgid='label_lti_secret',
                    label=_(u'Secret'),
                    description_msgid='help_lti_secret',
                    description=_(u'Secret used to verify LTI launch'),
                    ), 
                ),

    StringField('ltiLaunchUrl',
                required=True,
                widget=StringWidget(
                    label_msgid='label_lti_launch_url',
                    label=_(u'LTI Configuration URL'),
                    description_msgid='help_lti_launch_url',
                    description=_(u'URL that can be used by the Tool Consumer '
                                  'to directly launch this page.'),
                    ),
                ),


    StringField('ltiConfigUrl',
                required=True,
                widget=StringWidget(
                    label_msgid='label_lti_config_url',
                    label=_(u'LTI Configuration URL'),
                    description_msgid='help_lti_config_url',
                    description=_(u'URL that can be used by the Tool Consumer '
                                  'to configure LTI interactions as well as '
                                  'launch this page'),
                    ),
                ),

    StringField('ltiContactName',
                widget=StringWidget(
                    label_msgid='label_lti_contact_name',
                    label=_(u'Contact Name'),
                    description_msgid='help_lti_contact_name',
                    description=_(u'Name of persion that created the launch '
                                  'point.'),
                    ),
                ),

    StringField('ltiContactEmail',
                widget=StringWidget(
                    label_msgid='label_lti_contact_email',
                    label=_(u'Contact Email'),
                    description_msgid='help_lti_contact_email',
                    description=_(u'Email of person creating the launch '
                                  'point.'),
                    ),
                ),
))


class LtiLaunchParams(ATCTContent):
    '''
    Folder class for LTI Launch information
    '''

    implements(ILtiLaunchParams)
    schema = schema
    portal_type = 'LtiLaunchParams'

    _at_rename_after_creation = True


registerType(LtiLaunchParams, PROJECTNAME)
