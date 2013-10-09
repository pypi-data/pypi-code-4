# -*- coding: utf-8 -*-
#
# File: RDV_Proposition.py
#
# Copyright (c) 2008 by Ecreall
# Generator: ArchGenXML Version 2.2 (svn)
#            http://plone.org/products/archgenxml
#
# GNU General Public License (GPL)
#

__author__ = """Vincent Fretin <vincentfretin@ecreall.com>"""
__docformat__ = 'plaintext'

from AccessControl import ClassSecurityInfo
from Products.Archetypes.atapi import *
from zope.interface import implements
import interfaces

from Products.CMFDynamicViewFTI.browserdefault import BrowserDefaultMixin

from Products.rendezvous.config import *

##code-section module-header #fill in your manual code here
##/code-section module-header

copied_fields = {}
copied_fields['title'] = BaseSchema['title'].copy()
copied_fields['title'].required = 0
copied_fields['title'].write_permission = "rendezvous: write Proposition"
copied_fields['title'].widget.label = "A slot"
copied_fields['title'].widget.label_msgid = "rendezvous_Proposition_slot_label"
copied_fields['title'].widget.description = "A possible slot for this date"
copied_fields['title'].widget.description_msgid = "rendezvous_Proposition_slot_description"
copied_fields['title'].widget.i18n_domain = "rendezvous"
schema = Schema((

    copied_fields['title'],

    DateTimeField(
        name='date',
        widget=DateTimeField._properties['widget'](
            label="Date",
            label_msgid="rendezvous_Proposition_date_label",
            description="Possible date for the rendez-vous",
            description_msgid="rendezvous_Proposition_date_description",
            i18n_domain='rendezvous',
        ),
        required=1,
        write_permission="rendezvous: write Proposition",
    ),
    LinesField(
        name='available',
        widget=LinesField._properties['widget'](
            label="Members available",
            label_msgid="rendezvous_Proposition_available_label",
            description="List of participants who have checked this proposition",
            description_msgid="rendezvous_Proposition_available_description",
            visible=-1,
            i18n_domain='rendezvous',
        ),
    ),
    LinesField(
        name='unavailable',
        widget=LinesField._properties['widget'](
            label="Members unavailable",
            label_msgid="rendezvous_Proposition_unavailable_label",
            description="List of participants who haven't checked this proposition",
            description_msgid="rendezvous_Proposition_unavailable_description",
            visible=-1,
            i18n_domain='rendezvous',
        ),
    ),

),
)

##code-section after-local-schema #fill in your manual code here
##/code-section after-local-schema

RDV_Proposition_schema = BaseSchema.copy() + \
    schema.copy()

##code-section after-schema #fill in your manual code here
##/code-section after-schema

class RDV_Proposition(BaseContent, BrowserDefaultMixin):
    """
    """
    security = ClassSecurityInfo()

    implements(interfaces.IRDV_Proposition)

    meta_type = 'RDV_Proposition'
    _at_rename_after_creation = True

    schema = RDV_Proposition_schema

    ##code-section class-header #fill in your manual code here
    ##/code-section class-header

    # Methods

    security.declarePublic('manageParticipant')
    def manageParticipant(self, member_id, checked):
        """
        """
        available = list(self.getAvailable())
        unavailable = list(self.getUnavailable())
        if checked:
            if not member_id in available:
                available.append(member_id)
                self.setAvailable(available)
            if member_id in unavailable:
                unavailable.remove(member_id)
                self.setUnavailable(unavailable)
        else:
            if not member_id in unavailable:
                unavailable.append(member_id)
                self.setUnavailable(unavailable)
            if member_id in available:
                available.remove(member_id)
                self.setAvailable(available)


registerType(RDV_Proposition, PROJECTNAME)
# end of class RDV_Proposition

##code-section module-footer #fill in your manual code here
##/code-section module-footer



