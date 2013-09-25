# -*- coding: utf-8 -*-
#
# File: PM_Action.py
#
# Copyright (c) 2009 by []
# Generator: ArchGenXML Version 2.2 (svn)
#            http://plone.org/products/archgenxml
#
# GNU General Public License (GPL)
#

__author__ = """Michael Launay <michaellaunay@ecreall.com>"""
__docformat__ = 'plaintext'

from StringIO import StringIO
from DateTime import DateTime
from AccessControl import ClassSecurityInfo
from Products.Archetypes.atapi import *
from zope.interface import implements
import interfaces

from Products.CMFDynamicViewFTI.browserdefault import BrowserDefaultMixin

from Products.ATContentTypes.lib.calendarsupport import ICS_EVENT_START, vformat,\
    ICS_EVENT_END, rfc2445dt, foldLine
from Products.ATReferenceBrowserWidget.ATReferenceBrowserWidget import \
    ReferenceBrowserWidget
from Products.ATContentTypes.interfaces.interfaces import ICalendarSupport
from Products.ATContentTypes.content.folder import ATFolder
from Products.ATContentTypes.content.folder import ATFolderSchema
from Products.projectmanager.config import *

##code-section module-header #fill in your manual code here
from zope.component import getUtility
from Products.CMFCore.interfaces import ISiteRoot

from Products.CMFCore.utils import getToolByName

##/code-section module-header

copied_fields = {}
copied_fields['title'] = ATFolderSchema['title'].copy()
copied_fields['title'].write_permission = "PM : write action initial informations"
copied_fields['description'] = ATFolderSchema['description'].copy()
copied_fields['description'].required = 1
copied_fields['description'].write_permission = "PM : write action initial informations"
schema = Schema((

    copied_fields['title'],

    copied_fields['description'],

    TextField(
        name='mIntroduction',
        allowable_content_types=('text/plain', 'text/structured', 'text/html', 'application/msword',),
        widget=RichWidget(
            label="Introduction",
            label_msgid="PM_Action_Introduction_label",
            description="Presentation of the action",
            description_msgid="PM_Action_Introduction_description",
            i18n_domain='projectmanager',
        ),
        default_output_type='text/html',
        write_permission="PM : write action initial informations",
        read_permission="PM : read action informations",
    ),
    DateTimeField(
        name='mStartDate',
        widget=DateTimeField._properties['widget'](
            label="Start date",
            label_msgid="PM_Action_StartDate_label",
            description="Date of the work beginning",
            description_msgid="PM_Action_StartDate_description",
            i18n_domain='projectmanager',
        ),
        required=1,
        write_permission="PM : write action initial informations",
        read_permission="PM : read action informations",
    ),
    DateTimeField(
        name='mEstimatedEndDate',
        widget=DateTimeField._properties['widget'](
            label="Estimated end date",
            label_msgid="PM_Action_EstimatedEndDate_label",
            description="Expected date of the action completion",
            description_msgid="PM_Action_EstimatedEndDate_description",
            i18n_domain='projectmanager',
        ),
        required=1,
        write_permission="PM : write action initial informations",
        read_permission="PM : read action informations",
    ),
    DateTimeField(
        name='mEndDate',
        widget=DateTimeField._properties['widget'](
            label="End date",
            label_msgid="PM_Action_EndDate_label",
            description="Date of the action completion",
            description_msgid="PM_Action_EndDate_description",
            i18n_domain='projectmanager',
        ),
        write_permission="PM : write action final informations",
        read_permission="PM : read action informations",
    ),
    FloatField(
        name='mUsedTime',
        widget=FloatField._properties['widget'](
            label="Used time",
            label_msgid="PM_Action_UsedTime_label",
            description="Number of hour spended for the action",
            description_msgid="PM_Action_UsedTime_description",
            i18n_domain='projectmanager',
        ),
        write_permission="PM : write action final informations",
        read_permission="PM : read action informations",
    ),
    LinesField(
        name='mHumanRessources',
        widget=MultiSelectionWidget(
            label="Human ressources",
            label_msgid="PM_Action_HumanRessources_label",
            description="People who works",
            description_msgid="PM_Action_HumanRessources_description",
            i18n_domain='projectmanager',
        ),
        multiValued=1,
        vocabulary='getHumanRessources',
        required=1,
        write_permission="PM : write action initial informations",
        read_permission="PM : read action informations",
    ),
    ReferenceField(
        name='mPreviousAction',
        widget=ReferenceWidget(
            label="Previous actions",
            label_msgid="PM_Action_PreviousAction_label",
            description="Actions which must be completed before this one could begun",
            description_msgid="PM_Action_PreviousAction_description",
            i18n_domain='projectmanager',
        ),
        multiValued=1,
        relationship='Previous',
        vocabulary='getOtherActions',
        allowed_types=('PM_Action',),
        write_permission="PM : write action initial informations",
        read_permission="PM : read action informations",
    ),

),
)

##code-section after-local-schema #fill in your manual code here
##/code-section after-local-schema

PM_Action_schema = ATFolderSchema.copy() + \
    schema.copy()

##code-section after-schema #fill in your manual code here
##/code-section after-schema

class PM_Action(ATFolder):
    """ Action
    """
    security = ClassSecurityInfo()

    implements((interfaces.IPM_Action, ICalendarSupport))

    meta_type = 'PM_Action'
    _at_rename_after_creation = True

    schema = PM_Action_schema

    ##code-section class-header #fill in your manual code here
    ##/code-section class-header

    # Methods

    security.declarePublic('getOtherActions')
    def getOtherActions(self):
        """ return all other actions which are in the same Task
        """
        parent = self.getParentNode()
        actions = parent.objectValues(['PM_Action'])
        return [(obj.UID(), obj.Title()) for obj in actions if obj != self]

    security.declarePublic('guardRun')
    def guardRun(self):
        """ Check human ressources are setted
        """
        return self.getMHumanRessources()

    security.declarePublic('guardFinish')
    def guardFinish(self):
        """ Check if field are fill before transited
        """
        return self.getMEndDate()

    security.declarePublic('doRun')
    def doRun(self, state_change):
        """Promote human ressources to Worker
        and send email to human resources
        """
        ressources = self.getMHumanRessources()
        member_ids = []
        for human in ressources :
            member_id = human.split(':')[0]
            member_ids.append(member_id)
            self.manage_addLocalRoles(member_id, ['Worker'])
        self.reindexObject()

        template = getattr(self, 'PM_assignation_notification_template')

        self._sendMail(template=template,
                      addressees=member_ids,
                      state_change=state_change)

    security.declarePublic('doFinish')
    def doFinish(self, state_change):
        """Send notification to owner
        """
        template = getattr(self, 'PM_not_running_notification_template')
        object = state_change.object
        owner_info = object.owner_info()
        if owner_info :
            owner_id = owner_info['id']
            self._sendMail(template=template,
                           addressees=[owner_id],
                           state_change=state_change)

    security.declarePublic('doCancel')
    def doCancel(self,state_change):
        """Send notification to owner
        """
        template = getattr(self, 'PM_not_running_notification_template')
        object = state_change.object
        owner_info = object.owner_info()
        if owner_info :
            owner_id = owner_info['id']
            self._sendMail(template=template,
                           addressees=[owner_id],
                           state_change=state_change)

    security.declarePublic('doSuspend')
    def doSuspend(self,state_change):
        """Send notification to owner
        """
        template = getattr(self, 'PM_not_running_notification_template')
        object = state_change.object
        owner_info = object.owner_info()
        if owner_info :
            owner_id = owner_info['id']
            self._sendMail(template=template,
                           addressees=[owner_id],
                           state_change=state_change)

    # Manually created methods

    def _sendMail(self, template, state_change, addressees):
        portal = getToolByName(self, 'portal_url').getPortalObject()
        portal_groups = getToolByName(self, 'portal_groups')
        portal_membership = getToolByName(self, 'portal_membership')
        workflow = state_change.workflow
        actor_id = workflow.getInfoFor(self, 'actor', None)
        actor = portal_membership.getMemberById(actor_id)
        actor_fullname = actor.getProperty('fullname', 'no-name')
        actor_email = actor.getProperty('email', None)
        send = self.MailHost.send
        encoding = getUtility(ISiteRoot).getProperty('email_charset')
        email_from_address = self.email_from_address
        review_state = workflow.getInfoFor(self, 'review_state', None)

        for member_id in addressees :
            member = portal_membership.getMemberById(member_id)
            # a member could have been removed
            if member is not None:
                member_email = member.getProperty('email', None)
                member_name = member.getProperty('fullname', 'no-name')
                if member_email :
                    message = template(self, self.REQUEST,
                                        actor_fullname=actor_fullname,
                                        actor_email=actor_email,
                                        receipt_to_email=member_email,
                                        receipt_to_name=member_name,
                                        review_state=review_state)
                    send(message.encode(encoding))

    def start(self):
        """Start date is actions start date
        """
        return self.getMStartDate()

    def end(self):
        """End date is real end date if it has been set,
        else it is estimated end date
        """
        return self.getMEndDate() or self.getMEstimatedEndDate()


    security.declareProtected('View', 'getICal')
    def getICal(self):
        """get iCal data
        """
        out = StringIO()
        map = {
            'dtstamp'   : rfc2445dt(DateTime()),
            'created'   : rfc2445dt(DateTime(self.CreationDate())),
            'uid'       : self.UID(),
            'modified'  : rfc2445dt(DateTime(self.ModificationDate())),
            'summary'   : vformat(self.Title()),
            'startdate' : rfc2445dt(self.start()),
            'enddate'   : rfc2445dt(self.end()),
            }
        out.write(ICS_EVENT_START % map)

        description = self.Description()
        if description:
            out.write(foldLine('DESCRIPTION:%s\n' % vformat(description)))

        subject = self.Subject()
        if subject:
            out.write('CATEGORIES:%s\n' % ','.join(subject))

        # TODO  -- NO! see the RFC; ORGANIZER field is not to be used for non-group-scheduled entities
        #ORGANIZER;CN=%(name):MAILTO=%(email)
        #ATTENDEE;CN=%(name);ROLE=REQ-PARTICIPANT:mailto:%(email)

        cn = []
        mtool = getToolByName(self, 'portal_membership')
        human_resources = self.getMHumanRessources()
        if len(human_resources) > 0:
            human_resouce = human_resources[0]
            user_id = human_resouce.split(':')[0]
            user = mtool.getMemberById(user_id)
            contact_name = user.getProperty('fullname', user_id)
            cn.append(contact_name)

            contact_phone = user.getProperty('phone', '')
            if contact_phone:
                cn.append('')

            email = user.getProperty('email', '')
            if email:
                cn.append(email)
                out.write('CONTACT:%s\n' % vformat(', '.join(cn)))

        url = self.absolute_url()
        out.write('URL:%s\n' % url)
        out.write(ICS_EVENT_END)
        return out.getvalue()

    def getHumanResources(self):
        return [hr.split(':')[0] for hr in self.getMHumanRessources()]


registerType(PM_Action, PROJECTNAME)
# end of class PM_Action

##code-section module-footer #fill in your manual code here
##/code-section module-footer



