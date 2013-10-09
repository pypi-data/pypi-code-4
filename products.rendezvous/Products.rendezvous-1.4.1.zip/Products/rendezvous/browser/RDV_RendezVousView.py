# -*- coding: utf-8 -*-
#
# File: RDV_RendezVousView.py
#
# Copyright (c) 2008 by Ecreall
# Generator: ArchGenXML Version 2.2 (svn)
#            http://plone.org/products/archgenxml
#
# GNU General Public License (GPL)
#

__author__ = """Vincent Fretin <vincentfretin@ecreall.com>"""
__docformat__ = 'plaintext'

from DateTime import DateTime
##code-section module-header #fill in your manual code here
from plone.memoize.instance import memoize
from Products.CMFCore.utils import getToolByName
from zope.component import getUtility
from Products.CMFCore.interfaces import ISiteRoot
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from AccessControl import getSecurityManager
##/code-section module-header
from Acquisition import aq_inner
from Products.Five import BrowserView


class CloseRendezVous(BrowserView):

    def __call__(self):
        self.context.closed = True
        self.request.response.redirect(self.context.absolute_url())
        return u""

class ReopenRendezVous(BrowserView):

    def __call__(self):
        self.context.closed = False
        self.request.response.redirect(self.context.absolute_url())
        return u""


class RDV_RendezVousView(BrowserView):
    """
    """

    ##code-section class-header_RDV_RendezVousView #fill in your manual code here
    AVAILABLE = "available"
    UNAVAILABLE = "unavailable"
    UNKNOWN = "unknown"
    index = ViewPageTemplateFile("templates/RDV_RendezVousView.pt")

    def __call__(self, *args, **kw):
        return self.index(*args, **kw)
    ##/code-section class-header_RDV_RendezVousView

    @memoize
    def getPropositionsItemsByOrderedDates(self):
        context = self.context.aq_inner
        propositions_by_dates = context.getPropositionObjectsByDates()

        props = [{'label': date,
                  'props': self._getPropositions(propositions_by_dates, date),
                  'class': 'rendezvous-datechoice %s--%s' % (
                                     DateTime(date + ' ' + '09:00').ISO(),
                                     DateTime(date + ' ' + '17:00').ISO()),}
                  for date in sorted(propositions_by_dates.keys())]
        return props

    def _getIsoDateFromLabel(self, label):
        return DateTime(label).ISO()

    def _parse_hour(self, hour):
        hour = hour.replace(' ', '')
        hour = hour.replace('h', ':')
        hour = hour.replace('H', ':')
        hour, sep, minute = hour.partition(':')
        try:
            hour = int(hour)
            if hour > 24:
                return None
        except ValueError:
            return None
        try:
            minute = int(minute)
        except ValueError:
            minute = 0

        if minute > 59:
            minute = 0

        return "%2d:%2d" % (hour, minute)

    def _getKlassFromDateAndProposition(self, date, proposition):
        # separate two hours (can be separated by ' ' and '-'
        hourrange = proposition.replace(' ', '-')
        hourrange = [h for h in hourrange.split('-') if h]
        klass = ''
        hours = []
        for hour in hourrange:
            parsehour = self._parse_hour(hour)
            if parsehour:
                hours.append(parsehour)

        if len(hours) > 0:
            start = DateTime(date + ' ' + hours[0])
            if len(hours) > 1:
                end = DateTime(date + ' ' + hours[1])
            else:
                end = start + 1./24
            klass += 'rendezvous-datechoice %s--%s' % (start.ISO(), end.ISO())
        else:
            return self._getIsoDateFromLabel(date)

        return klass


    def _getPropositions(self, propositions_by_dates, date):
        propositions = []
        for proposition, uid in propositions_by_dates[date]:
            klass = self._getKlassFromDateAndProposition(date, proposition)
            propositions.append({'class': klass,
                                 'label': proposition,
                                 'participation': uid})
        return propositions

    def getParticipationClass(self, participant, proposition):
        prop_obj = getattr(self.context, proposition)
        if participant in prop_obj.getAvailable():
            return self.AVAILABLE
        if participant in prop_obj.getUnavailable():
            return self.UNAVAILABLE
        return self.UNKNOWN

    def addParticipation(self):
        context = self.context.aq_inner
        mtool = getToolByName(context, "portal_membership")
        actor = mtool.getAuthenticatedMember()
        participant = actor.getId()
        try:
            selected_propositions = self.request.form['propositions']
        except KeyError:
            selected_propositions = ()
        context.addParticipant(participant)
        for prop in self._getAllPropositionsIds():
            prop_obj = getattr(context, prop)
            checked = prop in selected_propositions
            prop_obj.manageParticipant(participant, checked)

        actor_fullname = actor.getProperty('fullname', participant)
        actor_email = actor.getProperty('email', None)
        encoding = getUtility(ISiteRoot).getProperty('email_charset')
        template = getattr(self.context, "rdv_participation_notification")
        owner = self.context.getOwner()
        owner_email = owner.getProperty('email', None)
        owner_name = owner.getProperty('fullname', owner.getId())
        if owner_email:
            message = template(self.context, self.request,
                                       actor_fullname=actor_fullname,
                                       actor_email=actor_email,
                                       receipt_to_email=owner_email,
                                       receipt_to_name=owner_name)
            self.context.MailHost.send(message.encode(encoding))

        self.request.response.redirect(self.context.absolute_url())

    def getFullname(self, member_id):
        portal_membership = getToolByName(self, "portal_membership")
        member = portal_membership.getMemberById(member_id)
        return member and member.getProperty("fullname") or member_id

    def getNbParticipantsForProposition(self, prop_id):
        return len(getattr(self.context, prop_id).getAvailable())

    def _getAllPropositionsIds(self):
        return [p['participation'] for date in self.getPropositionsItemsByOrderedDates()
                         for p in date['props']]

    def canModifyRendezvous(self):
        """Check if user can modify the rendezvous
        """
        context = aq_inner(self.context)
        sm = getSecurityManager()
        return sm.checkPermission('Modify portal content', context)

    def canCreateEvent(self):
        """Check if user can create an event
        """
        context = aq_inner(self.context)
        sm = getSecurityManager()
        return sm.checkPermission('Modify portal content', context) \
                and sm.checkPermission('ATContentTypes: Add Event',
                                       context.getParentNode())

    def rendezvous_create_event(self):
        dates = self.request['date'].split('--')
        query = 'type_name=Event&title=' + self.context.Title()
        if len(dates) >= 1:
            startdate = DateTime(dates[0].replace('-', '/').replace('T', ' '))
            query += '&startDate=' + str(startdate.strftime('%Y/%m/%d %H:%M'))
            if len(dates) == 2:
                enddate = DateTime(dates[1].replace('-', '/').replace('T', ' '))
            else:
                enddate = startdate + 1

            query += '&endDate=' + str(enddate.strftime('%Y/%m/%d %H:%M'))


        parent = aq_inner(self.context).getParentNode()
        uid = self.context.generateUniqueId('Event')
        url =  '%s/portal_factory/Event/%s/edit?%s' % (parent.absolute_url(), uid, query)
        self.request.response.redirect(url)

