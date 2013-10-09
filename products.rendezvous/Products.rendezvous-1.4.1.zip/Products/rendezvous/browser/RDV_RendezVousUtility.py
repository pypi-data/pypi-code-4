# -*- coding: utf-8 -*-
#
# File: RDV_RendezVousUtility.py
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
from Acquisition import aq_inner
import copy
##/code-section module-header


class RDV_RendezVousUtility:
    """
    """

    ##code-section class-header_RDV_RendezVousUtility #fill in your manual code here
    ##/code-section class-header_RDV_RendezVousUtility

    def getSelectedDates(view):
        """Return selected dates as list
        """
        context = aq_inner(view.context)
        request = view.request
        ctx_selected_dates = request.SESSION.get('rendezvous', {})
        uid = context.UID()
        if uid in ctx_selected_dates:
            return ctx_selected_dates[uid].keys()
        else:
            return context.getPropositionsByDates().keys()

    getSelectedDates = staticmethod(getSelectedDates)
    def toggleSelectedDate(view, selected_date):
        """Toogle selected date
        """
        selected_dates = RDV_RendezVousUtility.getPropositionsByDates(view)
        if not selected_date in selected_dates:
            selected_dates[selected_date] = []
        else:
            del selected_dates[selected_date]
        # save to session
        RDV_RendezVousUtility.setPropositionsByDates(view, selected_dates)

    toggleSelectedDate = staticmethod(toggleSelectedDate)
    def setPropositionsByDates(view, selected_dates):
        context = aq_inner(view.context)
        request = view.request
        uid = context.UID()
        session_rendezvous = request.SESSION.get('rendezvous', {})
        session_rendezvous[uid] = selected_dates
        request.SESSION['rendezvous'] = session_rendezvous

    setPropositionsByDates = staticmethod(setPropositionsByDates)
    def getPropositionsByDates(view):
        """Return a copy of selected dates with propositions
        """
        context = aq_inner(view.context)
        request = view.request
        ctx_selected_dates = request.SESSION.get('rendezvous', {})
        uid = context.UID()
        if uid in ctx_selected_dates:
            return copy.deepcopy(ctx_selected_dates[uid])
        else:
            return context.getPropositionsByDates()

    getPropositionsByDates = staticmethod(getPropositionsByDates)
    def getPropositionsByOrderedDates(view):
        propositions_by_dates = RDV_RendezVousUtility.getPropositionsByDates(view)
        return [(date, propositions_by_dates[date]) for date in sorted(propositions_by_dates.keys())]

    getPropositionsByOrderedDates = staticmethod(getPropositionsByOrderedDates)

##code-section module-footer #fill in your manual code here
##/code-section module-footer


