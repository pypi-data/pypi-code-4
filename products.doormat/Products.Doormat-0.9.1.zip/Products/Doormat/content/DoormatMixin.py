# -*- coding: utf-8 -*-
from AccessControl import ClassSecurityInfo
from Products.Archetypes import atapi
from Products.CMFDynamicViewFTI.browserdefault import BrowserDefaultMixin
from zope.interface import implements

import interfaces

schema = atapi.Schema((

    atapi.BooleanField(
        name='showTitle',
        default="True",
        widget=atapi.BooleanField._properties['widget'](
            label="Show title in viewlet",
            description="If checked, this Doormat / Column / Section's title "
                        "will be displayed in the doormat viewlet.",
            label_msgid='Doormat_label_showTitle',
            description_msgid='Doormat_help_showTitle',
            i18n_domain='Doormat',
        ),
    ),

),
)

DoormatMixin_schema = atapi.BaseSchema.copy() + \
    schema.copy()


class DoormatMixin(BrowserDefaultMixin):
    """
    """
    security = ClassSecurityInfo()

    implements(interfaces.IDoormatMixin)

    meta_type = 'DoormatMixin'
    _at_rename_after_creation = True

    schema = DoormatMixin_schema
