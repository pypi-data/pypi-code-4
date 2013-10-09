# -*- coding: utf-8 -*-
#
# File: RDV_RendezVousEdit.py
#
# Copyright (c) 2008 by Ecreall
# Generator: ArchGenXML Version 2.2 (svn)
#            http://plone.org/products/archgenxml
#
# GNU General Public License (GPL)
#

__author__ = """Vincent Fretin <vincentfretin@ecreall.com>"""
__docformat__ = 'plaintext'

##code-section module-header #fill in your manual code here
from DateTime import DateTime
from Products.CMFCore.utils import getToolByName
from plone.app.portlets.portlets.calendar import Renderer as CalRenderer
from plone.memoize.compress import xhtml_compress
from Acquisition import aq_inner
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.Five import BrowserView

from Products.rendezvous.browser.RDV_RendezVousUtility import RDV_RendezVousUtility


class _RDV_Calendar(CalRenderer):
    """overload the calendar for removing events
    """
    def __init__(self, context, request, view):
        self.context = context
        self.request = request
        self.view = view
        self.__parent__ = view

    def render(self):
        return xhtml_compress(self._template())

    def getDatesForCalendar(self):
        year = self.year
        month = self.month
        weeks_ = self.calendar.getWeeksList(month, year)
        selected_dates = self.view.getSelectedDates()
        weeks = []
        for week_ in weeks_:
            week = []
            for daynumber in week_:
                day = {}
                week.append(day)
                day['day'] = daynumber
                if daynumber == 0:
                    continue
                day['is_today'] = self.isToday(daynumber)
                day['date_string'] = '%d-%0.2d-%0.2d' % (year, month, daynumber)
                if day['date_string'] in selected_dates:
                    day['selected'] = True
                else:
                    day['selected'] = False
            weeks.append(week)
        return weeks
##/code-section module-header


class RDV_RendezVousEdit(BrowserView):
    """BrowserView
    """
    NB_COLUMNS = 5

    ##code-section class-header_RDV_RendezVousEdit #fill in your manual code here
    ##/code-section class-header_RDV_RendezVousEdit

    def getSelectedDates(self):
        return RDV_RendezVousUtility.getSelectedDates(self)

    def toggleSelectedDate(self, selected_date):
        return RDV_RendezVousUtility.toggleSelectedDate(self, selected_date)

    def getFormatedDates(self):
        return [self.context.toLocalizedTime(date) for date in sorted(self.getSelectedDates())]

    def __getattr__(self, key):
        try:
            return self.__dict__[key]
        except KeyError:
            return getattr(self.renderer, key)

    def getNbColumns(self):
        """Return the number of columns
        """
        propositionsbydates = RDV_RendezVousUtility.getPropositionsByDates(self)
        try:
            uid = self.context.aq_inner.UID()
            nb = self.request.SESSION['rendezvous']['nb_columns'][uid]
        except KeyError:
            nb = self.NB_COLUMNS
        for date, propositions in propositionsbydates.items():
            nb = max(len(propositions), nb)
        return nb

    def incNbColumns(self):
        uid = self.context.aq_inner.UID()
        session_rendezvous = self.request.SESSION.get('rendezvous', {})
        if not 'nb_columns' in session_rendezvous:
            session_rendezvous['nb_columns'] = {}
        session_rendezvous['nb_columns'][uid] = self.getNbColumns() + self.NB_COLUMNS
        self.request.SESSION['rendezvous'] = session_rendezvous

    def getPropositionsByOrderedDates(self):
        return RDV_RendezVousUtility.getPropositionsByOrderedDates(self)

    def saveChanges(self):
        context = aq_inner(self.context)
        request = self.request
        form = request.form

        # edit title

        title = 'title' in form and form.pop('title', False)
        if title: context.setTitle(title)
        finish = form.pop('finish', False)
        extend = form.pop('extend', False)

        # other form elements are dates
        propositions_by_dates = {}
        for date, propositions in request.form.items():
            propositions_by_dates[date] = [p for p in propositions if p]
            if not propositions_by_dates[date]:
                propositions_by_dates[date] = ['']

        # save in the session only
        RDV_RendezVousUtility.setPropositionsByDates(self, propositions_by_dates)
        if finish:
            # save to the filesystem
            context.setPropositionsByDates(propositions_by_dates)
            request.response.redirect(self.getNextURL())
        elif extend:
            self.incNbColumns()
            request.response.redirect(context.absolute_url() + '/edit_dates')

    def getNextURL(self):
        return aq_inner(self.context).absolute_url()

    def __init__(self, context, request):
        super(RDV_RendezVousEdit, self).__init__(context, request)
        date = request.form.pop('rdvdate', None)
        if date:
            self.toggleSelectedDate(date)

        self.renderer = _RDV_Calendar(context, request, self)
        self.portal_catalog = getToolByName(self.context, 'portal_catalog')
        self.renderer.update()

    index = ViewPageTemplateFile("templates/RDV_RendezVousEdit.pt")

    def __call__(self):
        if self.request.get('ajax', 0):
            plone_view = self.context.restrictedTraverse('@@plone')
            return "'%s'" % plone_view.toLocalizedTime(DateTime(self.request['rdvdate']))
        else:
            return self.index()

##code-section module-footer #fill in your manual code here
##/code-section module-footer


