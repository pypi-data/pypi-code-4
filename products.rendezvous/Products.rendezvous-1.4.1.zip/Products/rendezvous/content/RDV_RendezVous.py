# -*- coding: utf-8 -*-
#
# File: RDV_RendezVous.py
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
from Products.CMFCore.utils import getToolByName
import md5
##/code-section module-header

schema = Schema((

    LinesField(
        name='participants',
        widget=LinesField._properties['widget'](
            label="Participants",
            label_msgid="rendezvous_RendezVous_participants_label",
            description="List of members who have participated",
            description_msgid="rendezvous_RendezVous_participants_description",
            visible=-1,
            i18n_domain='rendezvous',
        ),
    ),

),
)

##code-section after-local-schema #fill in your manual code here
##/code-section after-local-schema

RDV_RendezVous_schema = OrderedBaseFolderSchema.copy() + \
    schema.copy()

##code-section after-schema #fill in your manual code here
##/code-section after-schema

class RDV_RendezVous(OrderedBaseFolder, BrowserDefaultMixin):
    """
    """
    security = ClassSecurityInfo()

    implements(interfaces.IRDV_RendezVous)

    meta_type = 'RDV_RendezVous'
    _at_rename_after_creation = True

    schema = RDV_RendezVous_schema

    ##code-section class-header #fill in your manual code here
    closed = False
    ##/code-section class-header

    # Methods

    security.declarePublic('getMembers')
    def getMembers(self):
        """
        """
        pass

    security.declarePublic('getPropositionsByDates')
    def getPropositionsByDates(self):
        """Return propositions by dates
        """
        propositions_by_dates = {}
        for date, propositions in self.getPropositionObjectsByDates().items():
            propositions_by_dates[date] = []
            propositions_ = propositions_by_dates[date]
            for proposition in propositions:
                propositions_.append(proposition[0])
        return propositions_by_dates

    security.declarePublic('getPropositionObjectsByDates')
    def getPropositionObjectsByDates(self):
        """Return propositions by dates, example:
           {'2008-11-27': [('evening': 'prop-2008-11-27-md5hexdigest')]}
        """
        propositions_by_dates = {}
        for proposition in self.objectValues("RDV_Proposition"):
            datetime = proposition.getDate()
            date = '%0.4d-%0.2d-%0.2d' % (datetime.year(), datetime.month(), datetime.day())
            if not date in propositions_by_dates:
                propositions_by_dates[date] = []
            # we use a list of items instead of dict to keep order
            propositions_by_dates[date].append((proposition.Title(), proposition.getId()))
        return propositions_by_dates

    security.declarePublic('setPropositionsByDates')
    def setPropositionsByDates(self, propositions_by_dates):
        """Create or update RDV_Proposition objects contained in this RDV_RendezVous
        """
        proposition_objects_by_dates = self.getPropositionObjectsByDates()
        portal_workflow = getToolByName(self, "portal_workflow")
        for date in sorted(propositions_by_dates.keys()):
            propositions = propositions_by_dates[date]
            for proposition in propositions:
                if date not in proposition_objects_by_dates or proposition not in dict(proposition_objects_by_dates[date]):
                    prop_id = self.invokeFactory('RDV_Proposition', 'prop-%s-%s' % (date, md5.md5(proposition).hexdigest()))
                    prop = getattr(self, prop_id)
                    prop.setTitle(proposition)
                    prop.setDate(date)
                    portal_workflow.doActionFor(prop, 'show')
                #else: we do nothing because proposition already exist
        # now delete objects not used
        objects2delete = []
        for date, propositions in proposition_objects_by_dates.items():
            if date not in propositions_by_dates:
                objects2delete.extend([p for p in dict(propositions).values()])
            else:
                for proposition in dict(propositions):
                    if proposition not in propositions_by_dates[date]:
                        objects2delete.append(dict(proposition_objects_by_dates[date])[proposition])
        if objects2delete:
            self.manage_delObjects(objects2delete)

    security.declarePublic('addParticipant')
    def addParticipant(self, member_id):
        """Add member_id to the participants list
        """
        if member_id in self.getParticipants():
            return
        participants = list(self.getParticipants())
        participants.append(member_id)
        self.setParticipants(participants)


registerType(RDV_RendezVous, PROJECTNAME)
# end of class RDV_RendezVous

##code-section module-footer #fill in your manual code here
##/code-section module-footer



