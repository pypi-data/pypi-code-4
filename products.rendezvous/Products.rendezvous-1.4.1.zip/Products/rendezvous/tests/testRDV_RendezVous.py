# -*- coding: utf-8 -*-
from Products.rendezvous.browser.RDV_RendezVousEdit import RDV_RendezVousEdit
from Products.rendezvous.browser.RDV_RendezVousView import RDV_RendezVousView

from ..testing import IntegrationTestCase


class testRDV_RendezVous(IntegrationTestCase):

    def setUp(self):
        super(testRDV_RendezVous, self).setUp()
        self.portal.REQUEST.SESSION = {}
        rdv_id = self.portal.invokeFactory('RDV_RendezVous', 'rdv1')
        self.rdv = getattr(self.portal, rdv_id)
        self.portal.portal_membership.addMember("johndoe", "passwd", ['Member'], [], properties={'name': 'John Doe', 'email': 'johndoe@example.com'})
        self.johndoe = self.portal.portal_membership.getMemberById('johndoe')

    def test_DelDateWithPropositions(self):
        propositions = self._create_propositions()
        # remove one date
        expected_propositions = {'2008-11-28':['8:30'],
                                 '2008-11-29':[''],
        }
        self.rdv.setPropositionsByDates(expected_propositions)
        self.assertEqual(expected_propositions, self.rdv.getPropositionsByDates())

    def test_AddDate(self):
        request = self.portal.REQUEST
        view = RDV_RendezVousEdit(self.rdv, request)
        self.assertEqual([], view.getSelectedDates())
        request.form['rdvdate'] = '2008-11-27'
        view = RDV_RendezVousEdit(self.rdv, request)
        self.assertEqual(['2008-11-27'], view.getSelectedDates())
        request.form['rdvdate'] = '2008-11-28'
        view = RDV_RendezVousEdit(self.rdv, request)
        self.assertEqual(['2008-11-27', '2008-11-28'], view.getSelectedDates())
        request.form['rdvdate'] = '2008-11-29'
        view = RDV_RendezVousEdit(self.rdv, request)
        self.assertEqual(['2008-11-27', '2008-11-28', '2008-11-29'], view.getSelectedDates())

    def test_manage_participants_in_proposition(self):
        prop_id = self.rdv.invokeFactory('RDV_Proposition', 'prop')
        prop = getattr(self.rdv, prop_id)
        prop.manageParticipant('johndoe', checked=True)
        self.assertEqual(('johndoe',), prop.getAvailable())
        prop.manageParticipant('johnsmith', True)
        self.assertEqual(('johndoe', 'johnsmith'), prop.getAvailable())
        prop.manageParticipant('johndoe', False)
        self.assertEqual(('johnsmith',), prop.getAvailable())

    def test_SaveChanges(self):
        request = self.portal.REQUEST
        view = RDV_RendezVousEdit(self.rdv, request)
        props = {'2008-12-25': ['12:00', 'minuit', 'midi', '', ''],
                 '2008-12-19': ['13:00', '14:00', '', '', ''],
                 '2008-12-31': ['', '', '', '', ''] }
        request.form = props
        request.form['finish'] = 'Finish'
        view.saveChanges()
        self.assertEqual({'2008-12-25': ['12:00', 'minuit', 'midi'],
                           '2008-12-19': ['13:00', '14:00'],
                            '2008-12-31': ['']}, self.rdv.getPropositionsByDates())

    def _create_propositions(self):
        propositions = {'2008-11-27':['morning', 'evening'],
                        '2008-11-28':['8:30'],
                        '2008-11-29':[''],
        }

        self.rdv.setPropositionsByDates(propositions)
        return propositions

    def test_SetPropositions(self):
        propositions = self._create_propositions()
        self.assertEqual(propositions, self.rdv.getPropositionsByDates())

    def test_reedit_rendezvous(self):
        propositions = self._create_propositions()
        request = self.portal.REQUEST
        view = RDV_RendezVousEdit(self.rdv, request)
        self.assertEqual(propositions.keys(), view.getSelectedDates())

    def test_NbColumns(self):
        request = self.portal.REQUEST
        view = RDV_RendezVousEdit(self.rdv, request)
        self.assertEqual(view.NB_COLUMNS, view.getNbColumns())

    def test_incColumns(self):
        request = self.portal.REQUEST
        request.form['extend'] = 'Extends columns'
        view = RDV_RendezVousEdit(self.rdv, request)
        self.assertEqual(view.NB_COLUMNS, view.getNbColumns())
        view.saveChanges()
#        view.incNbColumns()
        self.assertEqual(view.NB_COLUMNS*2, view.getNbColumns())

    def test_DelDate(self):
        request = self.portal.REQUEST
        # add two dates
        request.form['rdvdate'] = '2008-11-27'
        view = RDV_RendezVousEdit(self.rdv, request)
        request.form['rdvdate'] = '2008-11-28'
        view = RDV_RendezVousEdit(self.rdv, request)
        self.assertEqual(['2008-11-27', '2008-11-28'], view.getSelectedDates())
        # remove one date
        request.form['rdvdate'] = '2008-11-27'
        view = RDV_RendezVousEdit(self.rdv, request)
        self.assertEqual(['2008-11-28'], view.getSelectedDates())

    def test_add_other_dates(self):
        propositions = self._create_propositions()
        request = self.portal.REQUEST
        request.form['rdvdate'] = '2008-11-30'
        view = RDV_RendezVousEdit(self.rdv, request)
        self.assertEqual(sorted(list(propositions.keys()) + ['2008-11-30']), sorted(view.getSelectedDates()))

    def test_add_participant(self):
        self.rdv.addParticipant('johndoe')
        self.assertEqual(('johndoe',), self.rdv.getParticipants())

    def test_add_participant_twice(self):
        self.rdv.addParticipant('johndoe')
        self.rdv.addParticipant('johndoe')
        self.assertEqual(('johndoe',), self.rdv.getParticipants())

    def test_addParticipant(self):
        request = self.portal.REQUEST
        view = RDV_RendezVousEdit(self.rdv, request)
        props = {'2008-12-25': ['12:00', 'minuit', 'midi', '', ''],
                 '2008-12-19': ['13:00', '14:00', '', '', ''],
                 '2008-12-31': ['', '', '', '', ''] }
        request.form = props
        request.form['finish'] = 'Finish'
        view.saveChanges()
        request = self.portal.REQUEST
        self.login('johndoe')
        propositions = self.rdv.getPropositionObjectsByDates()
        request.form = {'propositions': (propositions['2008-12-25'][0][1],)}
        view = RDV_RendezVousView(self.rdv, request).addParticipation()
        prop = getattr(self.rdv, propositions['2008-12-25'][0][1])
        self.assertEqual(prop.getAvailable(), ('johndoe',))
        self.assertEqual(prop.getUnavailable(), ())
