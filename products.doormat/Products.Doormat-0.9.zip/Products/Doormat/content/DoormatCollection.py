# -*- coding: utf-8 -*-
from AccessControl import ClassSecurityInfo
from Products.Archetypes import atapi
from Products.ATContentTypes.content.base import ATCTContent
from Products.CMFDynamicViewFTI.browserdefault import BrowserDefaultMixin
from Products.Doormat.config import PROJECTNAME
from archetypes.referencebrowserwidget.widget import ReferenceBrowserWidget
from zope.interface import implements

import interfaces

schema = atapi.Schema((

    atapi.ReferenceField(
        name='collection',
        widget=ReferenceBrowserWidget(
            label='Collection',
            label_msgid='Doormat_label_collection',
            i18n_domain='Doormat',
        ),
        allowed_types="('Topic', 'Collection')",
        relationship="internally_references_to_collection",
    ),
    atapi.ReferenceField(
        name='showMoreLink',
        widget=ReferenceBrowserWidget(
            label=""""Show more" link""",
            description="Optionally, add a location for an extra link that "
                        "will be displayed below the items, like a link to "
                        "the collection itself.",
            label_msgid='Doormat_label_showMoreLink',
            description_msgid='Doormat_help_showMoreLink',
            i18n_domain='Doormat',
        ),
        relationship="more_link_links_to_internal",
    ),
    atapi.StringField(
        name='showMoreText',
        widget=atapi.StringField._properties['widget'](
            label=""""Show more" text""",
            description="""The text for the "Show more" link.""",
            label_msgid='Doormat_label_showMoreText',
            description_msgid='Doormat_help_showMoreText',
            i18n_domain='Doormat',
        ),
    ),
    atapi.IntegerField(
        name='limit',
        widget=atapi.IntegerField._properties['widget'](
            label="Limit number of items",
            description="Maximum number of items to be shown, leave blank for "
                        "all items.",
            label_msgid='Doormat_label_limit',
            description_msgid='Doormat_help_limit',
            i18n_domain='Doormat',
        ),
    ),
    atapi.BooleanField(
        name='showTime',
        widget=atapi.BooleanField._properties['widget'](
            label="Show time",
            description="Show the item's last modification time",
            label_msgid='Doormat_label_showTime',
            description_msgid='Doormat_help_showTime',
            i18n_domain='Doormat',
        ),
    ),

),
)

DoormatCollection_schema = atapi.BaseSchema.copy() + \
    schema.copy()


class DoormatCollection(ATCTContent, BrowserDefaultMixin):
    """
    """
    security = ClassSecurityInfo()

    implements(interfaces.IDoormatCollection)

    meta_type = 'DoormatCollection'
    _at_rename_after_creation = True

    schema = DoormatCollection_schema


atapi.registerType(DoormatCollection, PROJECTNAME)
