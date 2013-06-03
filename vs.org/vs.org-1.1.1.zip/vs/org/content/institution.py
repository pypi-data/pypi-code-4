################################################################
# vs.org (C) 2011, Veit Schiele
################################################################

# $Id: institution.py 2987 2011-03-16 14:55:06Z carsten $

"""
Definition of the Institution content type
"""

from AccessControl import ClassSecurityInfo
from zope.interface import implements

from archetypes.referencebrowserwidget.widget import ReferenceBrowserWidget
from pycountry import pycountry as pycountry
from compatible import atapi
from Products.ATContentTypes.configuration import zconf
from Products.ATContentTypes.content import folder
from Products.ATContentTypes.content import schemata
from Products.ATContentTypes.lib.constraintypes import ConstrainTypesMixinSchema
from Products.CMFCore.permissions import View
from Products.CMFCore.utils import getToolByName
from Products.MasterSelectWidget.MasterSelectWidget import MasterSelectWidget

from .. import orgMessageFactory as _
from ..interfaces import IBase
from ..interfaces import IInstitution
from ..config import PROJECTNAME
from base import BaseSchema
from numbers import NumbersMixin

from Products.ATVocabularyManager.namedvocabulary import NamedVocabulary
from Products.DataGridField import DataGridField, DataGridWidget, FixedRow
from Products.DataGridField.Column import Column

# define slave parameters for master
slave_fields = ({'name': 'province',
                 'action': 'vocabulary',
                 'vocab_method': 'getProvinceVocabulary',
                 'control_param': 'master',
                 },)

InstitutionSchema = folder.ATFolderSchema.copy() + ConstrainTypesMixinSchema.copy() + BaseSchema.copy() + atapi.Schema((

    atapi.TextField('text',
        required=False,
        searchable=True,
        primary=True,
        storage = atapi.AnnotationStorage(),
        validators = ('isTidyHtmlWithCleanup',),
        default_output_type='text/x-html-safe',
        widget = atapi.RichWidget(
            description='',
            label=_(u'label_body_text', default=u'Body Text'),
            rows=25,
            allow_file_upload=zconf.ATDocument.allow_document_upload),
    ),

    atapi.ReferenceField(
        name='employees',
        keepReferencesOnCopy=1,
        multiValued=1,
        allowed_types=('Employee',),
        relationship='isEmployee',
        widget=ReferenceBrowserWidget(
            show_review_state=1,
            allow_sorting=1,
            label=_(u'label_employees',),
        ),
    ),

    atapi.LinesField(
        'businessArea',
        accessor='BusinessArea',
        multiValued=1,
        searchable=True,
        storage=atapi.AnnotationStorage(),
        widget=atapi.KeywordWidget(
            label=_(u"label_businessArea"),
            description=_(u"help_businessArea"),
        ),
    ),


    DataGridField(
        'addresses',
        searchable=True,
        allow_empty_rows=False,
        allow_oddeven=True,
        storage=atapi.AnnotationStorage(),
        columns=('street','poBox','zipCode','city', 'geocode'),
        widget=DataGridWidget(
            label=_(u'label_addresses',),
            description=_(u'help_addresses',),
            columns = {
                    'street':   Column(_(u'label_street')),
                    'poBox':    Column(_(u'label_poBox')),
                    'zipCode':  Column(_(u'label_zipCode')),
                    'city':     Column(_(u'label_city')),
                    'geocode':  Column(_(u'label_geocode')),
            },
        ),
        validators=('isVSAddress',),
    ),


    atapi.StringField(
        'country',
        required=True,
        default='Select country...',
        vocabulary='getCountryVocabulary',
        storage=atapi.AnnotationStorage(),
        # could avoid importing, alas does not work
        # i18n_domain='plone',
        widget=MasterSelectWidget(
            slave_fields=slave_fields,
            label=_(u"label_country"),
            description=_(u"help_country"),
       ),
    ),


    atapi.StringField(
        'province',
        required=True,
        default='',
        vocabulary=[],
        storage=atapi.AnnotationStorage(),
        widget=atapi.SelectionWidget(
            label=_(u"label_province"),
            description=_(u"help_province"),
            format='select',
        ),
    ),


    atapi.TextField(
        'directions',
        required=False,
        searchable=True,
        storage=atapi.AnnotationStorage(),
        validators=('isTidyHtmlWithCleanup',),
        default_output_type='text/x-html-safe',
        widget=atapi.RichWidget(
            label=_(u"label_directions"),
            description=_(u"help_directions"),
        ),
    ),

))

InstitutionSchema['title'].storage = atapi.AnnotationStorage()
InstitutionSchema['description'].storage = atapi.AnnotationStorage()
InstitutionSchema['text'].storage = atapi.AnnotationStorage()

schemata.finalizeATCTSchema(
    InstitutionSchema,
    folderish=True,
    moveDiscussion=False
)

class Institution(folder.ATFolder, NumbersMixin):
    """Institution with addresses, phone numbers etc."""
    security = ClassSecurityInfo()
    implements(IInstitution, IBase)
    meta_type = "Institution"
    numbers_vocabulary = 'number_types_institution'
    schema = InstitutionSchema

    title = atapi.ATFieldProperty('title')
    description = atapi.ATFieldProperty('description')
    directions = atapi.ATFieldProperty('directions')
    addresses = atapi.ATFieldProperty('addresses')
    businessArea = atapi.ATFieldProperty('businessArea')
    country = atapi.ATFieldProperty('country')
    province = atapi.ATFieldProperty('province')

    security.declareProtected(View, 'getInstitution')
    def getInstitution(self):
        """ return Institution """
        return self

    def at_post_edit_script(self, *args, **kw):
        """ Filter out empty number fields """
        super(Institution, self).at_post_edit_script(*args, **kw)
        numbers = self.getNumbers()
        numbers = [d for d in numbers if d['number']]
        self.setNumbers(numbers)

    def getCountryVocabulary(self):
        """ Return countries from pycountry. The country list
            can be filtered by adding the related country codes to
            portal_properties.vsorg_properties.allowedCountryCodes.
        """

        pprop = getToolByName(self, 'portal_properties')
        vsprop = getToolByName(pprop, 'vsorg_properties')
        allowed_codes = vsprop.allowedCountryCodes
        allowed_codes = [code.lower().strip() for code in allowed_codes]
        result = atapi.DisplayList()
        result.add(u'', _(u'please_select_a_country'))
        for country in pycountry.countries:
            if allowed_codes and not country.alpha2.lower() in allowed_codes:
                continue
            result.add(country.alpha2, country.name)
        return result

    def getProvinceVocabulary(self, master):
        """ Return corresponding provinces """ 
        try: 
            subdivisions = list(pycountry.subdivisions.get(country_code=master))
        except KeyError:
            subdivisions = []
        result = list()
        for subdiv in subdivisions:
            result.append((subdiv.code, subdiv.name))
        result.sort(lambda x,y: cmp(x[1], y[1]))
        result.insert(0, (u'', _(u'please_select_a_province')))
        return atapi.DisplayList(result)

atapi.registerType(Institution, PROJECTNAME)
